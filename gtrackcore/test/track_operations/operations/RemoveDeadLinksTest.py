import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track_operations.Genome import Genome


from gtrackcore.track_operations.operations.RemoveDeadLinks import \
    RemoveDeadLinks
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class RemoveDeadLinksTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chr1Small = (GenomeRegion('hg19', 'chr1', 0, 3))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, starts=None, ends=None, values=None, strands=None,
                 ids=None, edges=None, weights=None, newId=None,
                 expStarts=None, expEnds=None, expValues=None,
                 expStrands=None, expIds=None, expEdges=None,
                 expWeights=None, expExtras=None, customChrLength=None,
                 allowOverlap=True, resultAllowOverlap=False,
                 expTrackFormatType=None, debug=False):

        track = createSimpleTestTrackContent(startList=starts, endList=ends,
                                             valList=values,
                                             strandList=strands,
                                             idList=ids, edgeList=edges,
                                             weightsList=weights,
                                             customChrLength=customChrLength)

        r = RemoveDeadLinks(track, newId=newId,
                            resultAllowOverlap=resultAllowOverlap,
                            debug=debug)

        result = r.calculate()
        self.assertTrue(result is not None)

        resFound = False

        for (k, v) in result.getTrackViews().iteritems():
            if cmp(k, self.chr1) == 0 or cmp(k, self.chr1Small) == 0:
                # All test tracks are in chr1
                resFound = True

                newStarts = v.startsAsNumpyArray()
                newEnds = v.endsAsNumpyArray()
                newValues = v.valsAsNumpyArray()
                newStrands = v.strandsAsNumpyArray()
                newIds = v.idsAsNumpyArray()
                newEdges = v.edgesAsNumpyArray()
                newWeights = v.weightsAsNumpyArray()
                newExtras = v.allExtrasAsDictOfNumpyArrays()

                if debug:
                    print("newTrackFormatType: {}".format(v.trackFormat))
                    print("expTrackFormatType: {}".format(expTrackFormatType))
                    print("newStarts: {}".format(newStarts))
                    print("expStarts: {}".format(expStarts))
                    print("newEnds: {}".format(newEnds))
                    print("expEnds: {}".format(expEnds))
                    print("newStrands: {}".format(newStrands))
                    print("expStrands: {}".format(expStrands))
                    print("newIds: {}".format(newIds))
                    print("expIds: {}".format(expIds))
                    print("newEdges: {}".format(newEdges))
                    print("expEdges: {}".format(expEdges))
                    print("newWeights: {}".format(newWeights))
                    print("expWeights: {}".format(expWeights))

                if expTrackFormatType is not None:
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)

                if expEnds is None and expStarts is not None:
                    # Assuming a point type track. Creating the expected ends.
                    expEnds = np.array(expStarts) + 1

                if expStarts is not None:
                    self.assertTrue(newStarts is not None)
                    self.assertTrue(np.array_equal(newStarts, expStarts))
                else:
                    self.assertTrue(newStarts is None)

                if expEnds is not None:
                    self.assertTrue(newEnds is not None)
                    self.assertTrue(np.array_equal(newEnds, expEnds))
                else:
                    self.assertTrue(newEnds is None)

                if expValues is not None:
                    self.assertTrue(newValues is not None)
                    self.assertTrue(np.array_equal(newValues, expValues))
                else:
                    self.assertTrue(newValues is None)

                if expStrands is not None:
                    self.assertTrue(newStrands is not None)
                    self.assertTrue(np.array_equal(newStrands, expStrands))
                else:
                    self.assertTrue(newStrands is None)

                if expIds is not None:
                    self.assertTrue(newIds is not None)
                    self.assertTrue(np.array_equal(newIds, expIds))
                else:
                    self.assertTrue(newIds is None)

                if expEdges is not None:
                    self.assertTrue(newEdges is not None)
                    self.assertTrue(np.array_equal(newEdges, expEdges))
                else:
                    self.assertTrue(newEdges is None)

                if expWeights is not None:
                    # As weights can contain numpy.nan, we can not use the
                    # normal array_equal method.
                    # (np.nan == np.nan) == False
                    # Using the assert_equal instead which.

                    self.assertTrue(newWeights is not None)
                    try:
                        np.testing.assert_equal(newWeights, expWeights)
                    except AssertionError:
                        self.fail("Weights are not equal")
                else:
                    self.assertTrue(newWeights is None)

                if expExtras is not None:
                    for key in expExtras.keys():
                        self.assertTrue(v.hasExtra(key))

                        expExtra = expExtras[key]
                        newExtra = newExtras[key]
                        self.assertTrue(np.array_equal(newExtra, expExtra))
                else:
                    self.assertTrue(len(newExtras) == 0)

            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        self.assertTrue(resFound)

    def _runMultipleTest(self, t1Starts, t1Ends, t1Ids, t1Edges, t2Starts,
                         t2Ends, t2Ids, t2Edges, t1ExpStarts, t1ExpEnds,
                         t1ExpIds, t1ExpEdges, t2ExpStarts, t2ExpEnds,
                         t2ExpIds, t2ExpEdges, debug=False,
                         expTrackFormatType=None):
        """
        Run test on multiple chromosomes.
        :return:
        """

        chr2 = (GenomeRegion('hg19', 'chr2', 0,
                             GenomeInfo.GENOMES['hg19']['size']['chr2']))

        hg19 = Genome('hg19', GenomeInfo.GENOMES['hg19'])

        t1Starts = np.array(t1Starts)
        t1Ends = np.array(t1Ends)
        t1Ids = np.array(t1Ids)
        t1Edges = np.array(t1Edges)
        t2Starts = np.array(t2Starts)
        t2Ends = np.array(t2Ends)
        t2Ids = np.array(t2Ids)
        t2Edges = np.array(t2Edges)

        tv1 = TrackView(self.chr1, t1Starts, t1Ends, None, None, t1Ids,
                        t1Edges, None, borderHandling='crop',
                        allowOverlaps=False, extraLists=OrderedDict())

        tv2 = TrackView(chr2, t2Starts, t2Ends, None, None, t2Ids, t2Edges,
                        None, borderHandling='crop', allowOverlaps=False,
                        extraLists=OrderedDict())
        tvs = OrderedDict()
        tvs[self.chr1] = tv1
        tvs[chr2] = tv2
        track = TrackContents(hg19, tvs)

        r = RemoveDeadLinks(track, useGlobal=True)

        result = r.calculate()
        self.assertTrue(result is not None)

        chr1Found = False
        chr2Found = False
        for (k, v) in result.trackViews.iteritems():
            starts = v.startsAsNumpyArray()
            ends = v.endsAsNumpyArray()
            ids = v.idsAsNumpyArray()
            edges = v.edgesAsNumpyArray()

            if cmp(k, self.chr1) == 0:
                if debug:
                    print("newStarts: {}".format(starts))
                    print("t1ExpStarts: {}".format(t1ExpStarts))
                    print("newEnds: {}".format(ends))
                    print("t1ExpEnds: {}".format(t1ExpEnds))
                    print("newIds: {}".format(ids))
                    print("t1ExpIds: {}".format(t1ExpIds))
                    print("newEdges: {}".format(edges))
                    print("t1ExpEdges: {}".format(t1ExpEdges))

                if expTrackFormatType is not None:
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)


                self.assertTrue(np.array_equal(starts, t1ExpStarts))
                self.assertTrue(np.array_equal(ends, t1ExpEnds))
                self.assertTrue(np.array_equal(ids, t1ExpIds))
                self.assertTrue(np.array_equal(edges, t1ExpEdges))
                chr1Found = True

            elif cmp(k, chr2) == 0:
                if debug:
                    print("newStarts: {}".format(starts))
                    print("t2ExpStarts: {}".format(t2ExpStarts))
                    print("newEnds: {}".format(ends))
                    print("t2ExpEnds: {}".format(t2ExpEnds))
                    print("newIds: {}".format(ids))
                    print("t2ExpIds: {}".format(t2ExpIds))
                    print("newEdges: {}".format(edges))
                    print("t2ExpEdges: {}".format(t2ExpEdges))

                if expTrackFormatType is not None:
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)


                self.assertTrue(np.array_equal(starts, t2ExpStarts))
                self.assertTrue(np.array_equal(ends, t2ExpEnds))
                self.assertTrue(np.array_equal(ids, t2ExpIds))
                self.assertTrue(np.array_equal(edges, t2ExpEdges))
                chr2Found = True
            else:
                # Tests if all tracks no in chr1 have a size of 0.
                self.assertEqual(v.size, 0)

        self.assertTrue(chr1Found)
        self.assertTrue(chr2Found)

    def testPointsSimple(self):
        """
        Simple test
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'], edges=['8','3'],
                      expStarts=[10,20], expIds=['3','10'], expEdges=['','3'],
                      expTrackFormatType="Linked points", debug=True)

    def testMultipleEdges(self):
        """
        Test removing edges when there are multiple edges per id.
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','10']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3',''],['3','10']],
                      expTrackFormatType="Linked points")

    def testMultipleEdgesNotAtEnd(self):
        """
        Edge is not at the end of the list
        :return:
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['9','3'],['3','10']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3',''],['3','10']],
                      expTrackFormatType="Linked points")

    def testRemoveAllEdges(self):
        """
        Remove all edges
        :return:
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=['9','424'],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=['',''],
                      expTrackFormatType="Linked points")

    def testRemoveAllEdgesMultiple(self):
        """
        Remove all edges, lists
        :return:
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['9','43'],['43','424']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=['',''],
                      expTrackFormatType="Linked points")

    def testChangingEdgesLength(self):
        """
        All of the edge lists have one empty space. We can remove this and
        make the edges arrays smaller.
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','4']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3'],['3']],
                      expTrackFormatType="Linked points")

    def testChangingEdgesLengthRemoveHole(self):
        """
        Test removing all of the edges in a list
        :return:
        """

        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['34','4']],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3'],['']],
                      expTrackFormatType="Linked points")

    def testWithWeightsSimple(self):
        """
        Check that the corresponding weights are removed as well.

        Weights are always floats. np.nan is used for padding.
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'], edges=['8','3'],
                      weights=[[0.33], [3.31]], expStarts=[10,20],
                      expIds=['3','10'], expEdges=['','3'],
                      expWeights=[[np.nan], [3.31]],
                      expTrackFormatType="Linked points")

    def testWithWeightsList(self):
        """
        Test with list of edges/weights
        :return:
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','10']],
                      weights=[[1.,2.],[3.,4.]],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3',''],['3','10']],
                      expWeights=[[1.,np.nan],[3.,4.]],
                      expTrackFormatType="Linked points")

    def testWithWeightsListNotAtEnd(self):
        """
        Edge to remove in not at the end of the list
        :return:
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['9','3'],['3','10']],
                      weights=[[1.,3.],[4.,10,]],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3',''],['3','10']],
                      expWeights=[[3., np.nan],[4.,10.]],
                      expTrackFormatType="Linked points")

    def testWithWeightsChangeLength(self):
        """
        Change the length of the list
        :return:
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','4']],
                      weights=[[4.,3.3],[98.,13.4]],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3'],['3']],
                      expWeights=[[4.],[98.]],
                      expTrackFormatType="Linked points")

    def testWithWeightsChangeLengthRemoveHole(self):
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['34','4']],
                      weights=[[32.,4.],[23.,43.4]],
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3'],['']],
                      expWeights=[[32.],[np.nan]],
                      expTrackFormatType="Linked points")

    def testNewIds(self):
        """
        Test assigning a new id instead of removing the dead edge.
        :return: None
        """
        self._runTest(starts=[10,20], ids=['3','10'], edges=['8','3'],
                      newId="dead",
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=['dead','3'], debug=False,
                      resultAllowOverlap=True)

    def testNewIdsList(self):
        """
        Edge is list
        :return:
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['3','4']], newId='dead',
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3','dead'],['3','dead']],
                      resultAllowOverlap=True, debug=False)

    def testNewIdsListAll(self):
        """
        All edges on id are updated
        :return:
        """
        self._runTest(starts=[10,20], ids=['3','10'],
                      edges=[['3','9'],['34','4']], newId='dead',
                      expStarts=[10,20], expIds=['3','10'],
                      expEdges=[['3','dead'],['dead','dead']],
                      resultAllowOverlap=True, debug=False)

    def testGlobalIds(self):
        """
        Test using global ids.
        :return: None
        """

        t1Starts = [5,15]
        t1Ends = [10,20]
        t1Ids = ['1','2']
        t1Edges = ['2','1']

        t2Starts = [50,230]
        t2Ends = [100,500]
        t2Ids = ['3','4']
        t2Edges = ['4','1']

        t1ExpStarts = [5,15]
        t1ExpEnds = [10,20]
        t1ExpIds = ['1','2']
        t1ExpEdges = ['2','1']

        t2ExpStarts = [50,230]
        t2ExpEnds = [100,500]
        t2ExpIds = ['3','4']
        t2ExpEdges = ['4', '1']

        self._runMultipleTest(t1Starts=t1Starts, t1Ends=t1Ends, t1Ids=t1Ids,
                              t1Edges=t1Edges, t2Starts=t2Starts,
                              t2Ends=t2Ends, t2Ids=t2Ids, t2Edges=t2Edges,
                              t1ExpStarts=t1ExpStarts, t1ExpEnds=t1ExpEnds,
                              t1ExpIds=t1ExpIds, t1ExpEdges=t1ExpEdges,
                              t2ExpStarts=t2ExpStarts, t2ExpEnds=t2ExpEnds,
                              t2ExpIds=t2ExpIds, t2ExpEdges=t2ExpEdges,
                              expTrackFormatType="Linked segments", debug=True)

    # *** Test track type inputs ***
    def testInputLinkedValuedPoints(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(starts=[1,2], values=[1,2], ids=['1','2'],
                      edges=['2','4'], expStarts=[1,2], expValues=[1,2],
                      expIds=['1','2'],expEdges=['2', ''],
                      expTrackFormatType="Linked valued points")

    def testInputLinkedSegments(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(starts=[1,5], ends=[3,10], ids=['1','2'],
                      edges=['2','4'], expStarts=[1,5], expEnds=[3,10],
                      expIds=['1','2'],expEdges=['2', ''],
                      expTrackFormatType="Linked segments")

    def testInputLinkedValuedSegments(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(starts=[1,5], ends=[3,10], values=[1,2], ids=['1','2'],
                      edges=['2','4'], expStarts=[1,5], expEnds=[3,10],
                      expValues=[1,2], expIds=['1','2'],expEdges=['2', ''],
                      expTrackFormatType="Linked valued segments")

    def atestInputLinkedGenomePartitioning(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ends=[0,1,2], ids=['','1','2'], edges=['','2','4'],
                      expEnds=[1,3], expIds=['1','2'],
                      expEdges=['2', ''], customChrLength=3, debug=True)

    def atestInputLinkedStepFunction(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2'], edges=['2','8'], ends=[1,3],
                      values=[1,2], expValues=[1,2], expEnds=[1,3],
                      expIds=['1','2'], expEdges=['2', ''],
                      customChrLength=3, debug=True)

    def testInputLinkedFunction(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2','3'], edges=['2','3','5'],
                      values=[1,2,3], expValues=[1,2,3],
                      expIds=['1','2','3'],expEdges=['2', '3', ''],
                      customChrLength=3, expTrackFormatType="Linked "
                                                            "function",
                      debug=True)

    def testInputLinkedBasePairs(self):
        """
        Most of this is tested i the LP test. Mostly checking that adding
        columns does not change anything.
        :return:
        """
        self._runTest(ids=['1','2','3'], edges=['2','3','8'],
                      expIds=['1','2','3'], expEdges=['2', '3', ''],
                      customChrLength=3,
                      expTrackFormatType="Linked base pairs")

if __name__ == "__main__":
    unittest.main()
