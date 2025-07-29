# coding: utf-8
# cython: language_level=3, linetrace=True, binding=True

"""Bindings to ARAGORN, a (t|mt|tm)RNA gene finder.

Attributes:
    ARAGORN_VERSION (`str`): The version of ARAGORN currently wrapped
        in PyARAGORN.
    TRANSLATION_TABLES (`set` of `int`): A set containing all the
        translation tables supported by PyARAGORN.

Example:
    PyARAGORN can work on any DNA sequence stored in either a text or a
    byte array. To load a sequence from one of the common sequence formats,
    you can use an external dedicated library such as
    `Biopython <https://github.com/biopython/biopython>`_::

        >>> import gzip
        >>> import Bio.SeqIO
        >>> with gzip.open("CP001621.fna.gz", "rt") as f:
        ...     record = Bio.SeqIO.read(f, "fasta")

    Then use PyARAGORN to find the tRNA genes using the
    bacterial genetic code (translation table 11):

        >>> import pyaragorn
        >>> rna_finder = pyaragorn.RNAFinder(11, trna=True, tmrna=False)
        >>> for gene in rna_finder.find_rna(record.seq.encode()):
        ...     print(gene.anticodon, gene.amino_acid, gene.begin, gene.end)
        tag Leu 87124 87207
        ttt Lys 87210 87285
        ...

    The gene coordinates are 1-indexed, inclusive, similarly to
    `Pyrodigal <https://pyrodigal.readthedocs.io>`_ genes.

References:
    - Laslett, Dean, and Björn Canback.
      “ARAGORN, a program to detect tRNA genes and tmRNA genes in nucleotide
      sequences.” Nucleic acids research vol. 32,1 11-6. 2 Jan. 2004,
      :doi:`10.1093/nar/gkh152`. :pmid:`14704338`. :pmcid:`PMC373265`.
    - Laslett, Dean, and Björn Canbäck.
      “ARWEN: a program to detect tRNA genes in metazoan mitochondrial
      nucleotide sequences.” Bioinformatics (Oxford, England) vol. 24,2
      (2008): 172-5. :doi:`10.1093/bioinformatics/btm573`. :pmid:`18033792`.

"""

from cython.operator cimport postincrement, dereference
from cpython.bytes cimport PyBytes_FromStringAndSize
from cpython.exc cimport PyErr_CheckSignals
from cpython.unicode cimport (
    PyUnicode_KIND,
    PyUnicode_DATA,
    PyUnicode_1BYTE_KIND,
    PyUnicode_GET_LENGTH,
    # PyUnicode_READ,
)

from libc.stdio cimport FILE, fopen, fdopen, fclose, fprintf, fputc, stdout, stderr
from libc.stdlib cimport calloc, free
from libc.string cimport memcpy
from libc.stdint cimport intptr_t

cimport aragorn
from aragorn cimport csw, data_set, gene

# --- Helpers ------------------------------------------------------------------

cdef extern from * nogil:
    Py_UCS4 PyUnicode_READ(int kind, const void* data, size_t pos)

cdef extern from * nogil:
    """
    void default_sw(csw* sw) {
        csw x = {
            {"tRNA", "tmRNA", "", "", "CDS", "overall"},
            NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, STANDARD, 0,
            {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
            0, METAZOAN_MT, 1, 0, 5, 5, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0,
            3, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
            {0, 0, 0, 0, 0, 0}, 0, 0, 0, 0, NTAG, 10, 30,
            {0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0},
            0, 0, 0, 0, 0L, 100.0, 1.0, tRNAthresh, 4.0, 29.0, 26.0, 7.5, 8.0,
            mtRNAtthresh, mtRNAdthresh, mtRNAdtthresh, -7.9, -6.0, tmRNAthresh,
            14.0, 10.0, 25.0, 9.0, srpRNAthresh, CDSthresh,
            {tRNAthresh, tmRNAthresh, srpRNAthresh, 0.0, CDSthresh},
            {
                45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,
                45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 10, 65,
                82, 65, 71, 79, 82, 78, 32, 118, 49, 46, 50, 46, 52, 49, 32,
                32, 32, 68, 101, 97, 110, 32, 76, 97, 115, 108, 101, 116, 116,
                10, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,
                45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 10,
                TERM
            }
        };
        memcpy(sw, &x, sizeof(csw));
    }
    """
    void default_sw(csw* sw)

cdef inline long int sq(data_set* d, long int pos) nogil:
    return (pos + d.psmax - 1) % d.psmax + 1


# --- Constants ----------------------------------------------------------------

cdef set _TRANSLATION_TABLES  = set(range(1, 7)) | set(range(9, 17)) | set(range(21, 27)) | {29, 30} | {32, 33}

__version__ = PROJECT_VERSION

TRANSLATION_TABLES = _TRANSLATION_TABLES
ARAGORN_VERSION = PROJECT_ARAGORN_VERSION


# --- Classes ------------------------------------------------------------------

cdef class Gene:
    """A gene identified by ARAGORN.
    """

    cdef gene _gene
    cdef int  _genetic_code

    @staticmethod
    cdef Gene _new_gene(gene* _gene, int _genetic_code):
        cdef Gene obj

        if _gene.genetype == aragorn.tRNA:
            obj = TRNAGene.__new__(TRNAGene)
        elif _gene.genetype == aragorn.tmRNA:
            obj = TMRNAGene.__new__(TMRNAGene)
        else:
            raise NotImplementedError

        memcpy(&obj._gene, _gene, sizeof(gene))
        obj._genetic_code = _genetic_code
        return obj

    def __sizeof__(self):
        return sizeof(self)

    @property
    def type(self):
        return ["tRNA", "tmRNA", "", "", "CDS"][<int> self._gene.genetype]

    @property
    def begin(self):
        """`int`: The sequence coordinate at which the gene begins.

        Hint:
            This coordinate is 1-based, inclusive. To use it to index
            a Python array or string, subtract one.

        """
        return self._gene.start

    @property
    def end(self):
        """`int`: The sequence coordinate at which the gene end.

        Hint:
            This coordinate is 1-based, inclusive. To use it to index
            a Python array or string, subtract one.

        """
        return self._gene.stop

    @property
    def length(self):
        """`int`: The length of the RNA gene.
        """
        return aragorn.seqlen(&self._gene)

    @property
    def strand(self):
        """`int`: *-1* if the gene is on the reverse strand, *+1* otherwise.
        """
        return -1 if self._gene.comp else +1

    @property
    def energy(self):
        """`float`: The approximated energy of the RNA structure.
        """
        cdef csw sw
        default_sw(&sw) # FIXME?
        return aragorn.nenergy(&self._gene, &sw)

    def sequence(self):
        """Retrieve the full sequence of the RNA gene.
        """
        cdef int       i
        cdef int       l = aragorn.seqlen(&self._gene)
        cdef bytearray b = bytearray(l)
        for i in range(l):
            b[i] = aragorn.cpbase(self._gene.seq[i])
        return b.decode('ascii')


cdef class TRNAGene(Gene):
    """A transfer RNA (tRNA) gene.
    """

    @property
    def amino_acid(self):
        """`str`: The 3-letter amino-acid(s) for this gene.

        Hint:
            If the anticodon loop contains 6 or 8 bases, ``???`` is
            returned.

        """
        cdef csw sw
        cdef int* s = self._gene.seq + self._gene.anticodon
        (<int*> &sw.geneticcode)[0] = self._genetic_code
        if self._gene.cloop == 6 or self._gene.cloop == 8:
            return "???"
        else:
            return aragorn.aa(s, &sw).decode('ascii')

    @property
    def amino_acids(self):
        """`tuple` of `str`: All possible 3-letter amino-acids for this gene.

        Hint:
            If the anticodon loop contains 6 or 8 bases, a tuple of two
            amino-acid is returned, otherwise a tuple with a single element
            is returned.

        """
        cdef csw sw
        cdef int* s = self._gene.seq + self._gene.anticodon
        (<int*> &sw.geneticcode)[0] = self._genetic_code
        if self._gene.cloop == 6:
            return (
                aragorn.aa(s - 1, &sw).decode('ascii'),
                aragorn.aa(s, &sw).decode('ascii'),
            )
        elif self._gene.cloop == 8:
            return (
                aragorn.aa(s, &sw).decode('ascii'),
                aragorn.aa(s + 1, &sw).decode('ascii')
            )
        else:
            return aragorn.aa(s, &sw).decode('ascii')

    @property
    def anticodon(self):
        """`str`: The anticodon of the tRNA gene.
        """
        cdef tuple c
        cdef int*  s = self._gene.seq + self._gene.anticodon
        if self._gene.cloop == 6:
            c = ( aragorn.cbase(s[0]), aragorn.cbase(s[1]) )
        elif self._gene.cloop == 8:
            c = ( aragorn.cbase(s[0]), aragorn.cbase(s[1]), aragorn.cbase(s[2]), aragorn.cbase(s[3]) )
        else:
            c = ( aragorn.cbase(s[0]), aragorn.cbase(s[1]), aragorn.cbase(s[2]) )
        return ''.join(map(chr, c))

    @property
    def anticodon_offset(self):
        """`int`: The offset in the gene at which the anticodon starts.
        """
        cdef int x = 1 + self._gene.anticodon
        if self._gene.nintron > 0 and self._gene.intron <= self._gene.anticodon:
            x += self._gene.nintron
        return x

    @property
    def anticodon_length(self):
        """`int`: The length of the anticodon (in nucleotides).
        """
        if self._gene.cloop == 6:
            return 2
        elif self._gene.cloop == 8:
            return 4
        else:
            return 3


cdef class TMRNAGene(Gene):
    """A transfer-messenger RNA (tmRNA) gene.

    Example:
        >>> rna_finder = pyaragorn.RNAFinder(11, trna=False, tmrna=True)
        >>> tmrna = rna_finder.find_rna(str(record.seq))[0]
        >>> tmrna.begin, tmrna.end
        (198037, 198447)
        >>> tmrna.peptide()
        'AEKNEENFEMPAFMINNASAGANYMFA**'

    """

    @property
    def permuted(self):
        """`bool`: Whether this tmRNA gene is a permuted gene.
        """
        return self._gene.asst != 0

    @property
    def orf_offset(self):
        """`int`: The offset in the gene at which the open-reading frame starts.
        """
        return self._gene.tps + 1

    @property
    def orf_length(self):
        """`int`: The length of the open-reading frame (in nucleotides).
        """
        cdef int  tpe    = self._gene.tpe
        cdef int* se     = (self._gene.eseq + tpe) + 1
        cdef int* sb     = (self._gene.eseq + self._gene.tps)
        cdef int  stride = 3

        cdef csw sw
        (<int*> &sw.geneticcode)[0] = self._genetic_code

        while aragorn.ltranslate(se, &self._gene, &sw) == ord('*'):
            se += stride
            tpe += stride

        return tpe - self._gene.tps

    def orf(self, include_stop=True):
        """Retrieve the open-reading frame of the mRNA-like region.

        Arguments:
            include_stop (`bool`): Whether or not to include the STOP codons
                in the returned nucleotide sequence. Defaults to `True`.

        Returns:
            `str`: The sequence of the mRNA-like region in the tmRNA
            gene, optionally without STOP codons.

        """
        cdef int  tpe    = self._gene.tpe
        cdef int* se     = (self._gene.eseq + tpe) + 1
        cdef int* sb     = (self._gene.eseq + self._gene.tps)
        cdef int  stride = 3 if include_stop else -3

        cdef csw sw
        (<int*> &sw.geneticcode)[0] = self._genetic_code

        while aragorn.ltranslate(se, &self._gene, &sw) == ord('*'):
            se += stride
            tpe += stride

        cds = bytearray()
        while sb < se:
            cds.append(aragorn.cpbase(sb[0]))
            sb += 1

        return cds.decode('ascii')

    def peptide(self, include_stop=True):
        """Retrieve the peptide sequence of the mRNA-like region.

        Arguments:
            include_stop (`bool`): Whether or not to include the STOP codons
                in the returned peptide sequence. Defaults to `True`.

        Returns:
            `str`: The translation of the mRNA-like region of the tmRNA
            gene, optionally without STOP codons.

        """
        cdef int  tpe    = self._gene.tpe
        cdef int* se     = (self._gene.eseq + tpe) + 1
        cdef int* sb     = (self._gene.eseq + self._gene.tps)
        cdef int  stride = 3 if include_stop else -3

        cdef csw sw
        (<int*> &sw.geneticcode)[0] = self._genetic_code

        while aragorn.ltranslate(se, &self._gene, &sw) == ord('*'):
            se += stride
            tpe += stride

        peptide = bytearray()
        while sb < se:
            peptide.append(aragorn.ltranslate(sb, &self._gene, &sw))
            sb += 3

        return peptide.decode('ascii')


cdef class Cursor:
    cdef object      obj
    cdef const void* data
    cdef int         kind
    cdef size_t      length
    cdef data_set    ds

    def __init__(self, obj):
        cdef const unsigned char[::1] view
        if isinstance(obj, str):
            self.kind = PyUnicode_KIND(obj)
            self.data = PyUnicode_DATA(obj)
            self.length = PyUnicode_GET_LENGTH(obj)
        else:
            view = obj
            self.kind = PyUnicode_1BYTE_KIND
            self.data = &view[0]
            self.length = view.shape[0]

        # keep a reference to the data source
        self.obj = obj

        # reinitialize dataset book-keeping
        self.ds.filepointer = 0
        self.ds.ns = 0
        self.ds.nf = 0
        self.ds.nextseq = 0L
        self.ds.nextseqoff = 0L
        self.ds.seqstart = 0
        self.ds.seqstartoff = 0
        self.ds.ps = 0
        self.ds.psmax = self.length

        # count GC%
        self.ds.gc = self._gc()

    cdef int _forward(self) noexcept nogil:
        cdef Py_UCS4 x
        cdef int     base

        if self.ds.ps >= self.ds.psmax:
            return <int> aragorn.base.TERM

        x = PyUnicode_READ(self.kind, self.data, self.ds.ps)
        if x >= 128:
            return <int> aragorn.base.NOBASE

        base = aragorn.map[x]
        if base >= <int> aragorn.base.Adenine:
            self.ds.ps += 1
            return base
        else:
            return <int> aragorn.base.NOBASE

    cdef double _gc(self) noexcept nogil:
        cdef long    i
        cdef Py_UCS4 x
        cdef int     base
        cdef long    ngc  = 0
        cdef long    ps   = 0

        for i in range(self.length):
            x = PyUnicode_READ(self.kind, self.data, i)
            base = aragorn.map[x]
            if base == -1:
                break
            ngc += (base == <int> aragorn.base.Cytosine) or (base == <int> aragorn.base.Guanine)
            ps += 1

        return <double> ngc / <double> ps


cdef class RNAFinder:
    """A configurable RNA gene finder.
    """
    cdef csw _sw

    def __init__(
        self,
        int translation_table = 1,
        *,
        bint trna = True,
        bint tmrna = True,
        bint linear = False,
    ):
        """__init__(self, translation_table=1, *, trna=True, tmrna=True, linear=False)\n--\n

        Create a new RNA finder.

        Arguments:
            translation_table (`int`, optional): The translation table to
                use. Check the :wiki:`List of genetic codes` page
                listing all genetic codes for the available values, or
                the :attr:`pyaragorn.TRANSLATION_TABLES` constant for allowed
                values.

        """
        default_sw(&self._sw)
        self._sw.trna = trna
        self._sw.tmrna = tmrna
        self._sw.linear = linear
        self._sw.f = stdout
        self._sw.verbose = False #True

        if translation_table not in _TRANSLATION_TABLES:
            raise ValueError(f"invalid translation table: {translation_table!r}")
        self._sw.geneticcode = translation_table

    def find_rna(self, object sequence):
        """Find RNA genes in the input DNA sequence.

        Arguments:
            sequence (`str` or buffer): The nucleotide sequence to process,
                either as a string of nucleotides (upper- or lowercase), or
                as an object implementing the buffer protocol.

        Returns:
            `list` of `~pyaragorn.Gene`: A list of `~pyaragorn.Gene` (either
            `~pyaragorn.TRNAGene` or `~pyaragorn.TMRNAGene`) corresponding
            to RNA genes detected in the sequence according to the `RNAFinder`
            parameters.

        """
        cdef int      n
        cdef int      nt
        cdef csw      sw
        cdef int*     vsort  = NULL
        cdef Cursor   cursor = Cursor(sequence)

        # copy parameters to ensure the `find_rna` method is re-entrant
        memcpy(&sw, &self._sw, sizeof(csw))

        try:
            with nogil:
                # allocate memory for the result genes
                sw.genespace = aragorn.NT
                sw.genes = <gene*> calloc(sw.genespace, sizeof(gene))
                if sw.genes is NULL:
                    raise MemoryError("failed to allocate memory")
                # detect RNA genes with the "batched" algorithm
                nt = self._bopt(cursor, &sw)
                # allocate array for sorting genes
                vsort = <int*> calloc(nt, sizeof(int))
                if vsort is NULL:
                    raise MemoryError("failed to allocate memory")
                # sort and threshold genes
                n = aragorn.gene_sort(&cursor.ds, nt, vsort, &sw)
            # recover genes
            genes = []
            for i in range(n):
                genes.append(Gene._new_gene(&sw.genes[vsort[i]], sw.geneticcode))
        finally:
            free(vsort)
            free(sw.genes)

        return genes

    cdef int _bopt(
        self,
        Cursor cursor,
        csw* sw
    ) except -1 nogil:
        # adapted from bopt_fastafile to use with our own `Cursor` dataset
        cdef int nt
        cdef int seq[((2 * aragorn.LSEQ) + aragorn.WRAP) + 1]
        cdef int cseq[((2 * aragorn.LSEQ) + aragorn.WRAP) + 1]
        cdef int wseq[(2 * aragorn.WRAP) + 1]
        cdef long i
        cdef long rewind
        cdef long drewind
        cdef long tmaxlen
        cdef bint flag
        cdef int length
        cdef int *s
        cdef int *sf
        cdef int *se
        cdef int *sc
        cdef int *swrap
        cdef long gap
        cdef long start
        cdef bint loop
        cdef bint NX
        cdef bint SH

        # compute width of sliding windows
        rewind = aragorn.MAXTAGDIST + 20
        if sw.trna or sw.mtrna:
            tmaxlen = aragorn.MAXTRNALEN + sw.maxintronlen
            if rewind < tmaxlen:
                rewind = tmaxlen
        if sw.tmrna:
            if rewind < aragorn.MAXTMRNALEN:
                rewind = aragorn.MAXTMRNALEN
        if sw.peptide:
            if sw.tagthresh >= 5 and rewind < aragorn.TSWEEP:
                rewind = aragorn.TSWEEP

        sw.loffset = rewind
        sw.roffset = rewind
        drewind = 2 * rewind

        # cleanly initialize gene array
        aragorn.init_gene(sw.genes, 0, aragorn.NT)

        nt = 0
        flag = 0
        start = 1L

        loop = True
        NX = True
        SH = True

        se = seq
        if sw.linear:
            for i in range(rewind):
                postincrement(se)[0] = aragorn.NOBASE
            start -= rewind
        else:
            if cursor.ds.psmax <= drewind:
                gap = drewind - cursor.ds.psmax
                sc = se + gap
                while se < sc:
                    postincrement(se)[0] = aragorn.NOBASE

                swrap = wseq
                sc = se + cursor.ds.psmax
                while se < sc:
                    se[0] = cursor._forward()
                    postincrement(swrap)[0] = postincrement(se)[0]

                sc = swrap + gap
                while swrap < sc:
                    postincrement(swrap)[0] = aragorn.NOBASE

                swrap = wseq
                sc = swrap + cursor.ds.psmax
                while swrap < sc:
                    postincrement(se)[0] = postincrement(swrap)[0]

                swrap = wseq
                sc = swrap + drewind
                while swrap < sc:
                    postincrement(se)[0] = postincrement(swrap)[0]

                sw.loffset = drewind
                sw.roffset = drewind
                start -= drewind
                flag = 1
                # goto SH
                loop = True
                SH = True
                NX = False

            else:
                swrap = wseq
                sc = seq + drewind
                while se < sc:
                    se[0] = cursor._forward()
                    postincrement(swrap)[0] = postincrement(se)[0]

        # weird ass loop to emulate a GOTO
        while loop:

            # label NX: next
            sc = seq + aragorn.LSEQ
            if NX:
                while (se < sc):
                    postincrement(se)[0] = cursor._forward()
                    if cursor.ds.ps >= cursor.ds.psmax:
                        if sw.linear:
                            for i in range(rewind):
                                postincrement(se)[0] = aragorn.NOBASE
                        else:
                            sc = wseq + drewind
                            swrap = wseq
                            while (swrap < sc):
                                postincrement(se)[0] = postincrement(swrap)[0]
                        flag = 1
                        SH = True
                        break

            # label SH: search
            if SH:
                length = <int> (se - seq)

                with gil:
                    PyErr_CheckSignals()

                # if (sw.verbose):
                #     vstart = sq(d, start + sw.loffset)
                #     vstop = sq(d, ((start + length) - sw.roffset) - 1)
                #     if (vstop < vstart):
                #         fprintf(stderr, "Searching from %ld to %ld\n", vstart, d.psmax)
                #         fprintf(stderr, "Searching from 1 to %ld\n", vstop)
                #     else:
                #         fprintf(stderr, "Searching from %ld to %ld\n", vstart, vstop)

                if (sw.both != 1):
                    sw.start = start
                    sw.comp = 0
                    nt = aragorn.tmioptimise(&cursor.ds, seq, length, nt, sw)

                if (sw.both > 0):
                    aragorn.sense_switch(seq, cseq, length)
                    sw.start = start + length
                    sw.comp = 1
                    nt = aragorn.tmioptimise(&cursor.ds, cseq, length, nt, sw)

                if not flag:
                    s = seq
                    sf = se - drewind
                    se = seq + drewind
                    while (s < se):
                        postincrement(s)[0] = postincrement(sf)[0]
                    start += length - drewind
                    # goto NX
                    NX = SH = loop = True
                    continue

                if nt < 1:
                    cursor.ds.nf += 1
                if sw.maxintronlen > 0:
                    aragorn.remove_overlapping_trna(&cursor.ds, nt, sw)
                if sw.updatetmrnatags:
                    aragorn.update_tmrna_tag_database(sw.genes, nt, sw)

                # FIXME: here should sort genes and filter them with `gene_sort`
                # aragorn.batch_gene_set(d, nt, sw)

                # if sw.verbose:
                #     fprintf(stderr, "%s\nSearch Finished\n\n", d.seqname)

                cursor.ds.ns += 1
                # exit loop
                loop = False

        return nt

    # if (d.ns > 1) and (sw.batch < 2):
    #     fprintf(f, ">end \t%d sequences", d.ns)
    #     if sw.trna or sw.mtrna:
    #         fprintf(f, " %d tRNA genes", sw.ngene[<int> aragorn.tRNA])
    #     if sw.tmrna:
    #         fprintf(f, " %d tmRNA genes", sw.ngene[<int> aragorn.tmRNA])
    #     if d.nf > 0:
    #         sens = (100.0 * (d.ns - d.nf)) / d.ns
    #         fprintf(f, ", nothing found in %d sequences, (%.2lf%% sensitivity)", d.nf, sens)
    #     fputc('\n', f)
    # if sw.updatetmrnatags:
    #     aragorn.report_new_tmrna_tags(sw)
