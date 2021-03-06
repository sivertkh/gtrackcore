import unittest
import numpy as np
from collections import OrderedDict

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Subtract import Subtract
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.test.track_operations.TestUtils import createTrackView
from gtrackcore.test.track_operations.TestUtils import \
    createSimpleTestTrackContent


class SubtractTest(unittest.TestCase):

    def setUp(self):
        self.chr1 = (GenomeRegion('hg19', 'chr1', 0,
                                  GenomeInfo.GENOMES['hg19']['size']['chr1']))
        self.chromosomes = (GenomeRegion('hg19', c, 0, l)
                            for c, l in
                            GenomeInfo.GENOMES['hg19']['size'].iteritems())

    def _runTest(self, startsA=None, startsB=None, endsA=None, endsB=None,
                 strandsA=None, strandsB=None, valsA=None, valsB=None,
                 idsA=None, idsB=None, edgesA=None, edgesB=None,
                 weightsA=None, weightsB=None, extrasA=None, extrasB=None,
                 expStarts=None, expEnds=None, expStrands=None, expVals=None,
                 expIds=None, expEdges=None, expWeights=None, expExtras=None,
                 expNoResult=False, expTrackFormatType=None,
                 customChrLength=None, resultAllowOverlap=False,
                 useStrands=True, treatMissingAsNegative=False, debug=False):

        track1 = createSimpleTestTrackContent(startList=startsA,
                                              endList=endsA, valList=valsA,
                                              strandList=strandsA,
                                              idList=idsA, edgeList=edgesA,
                                              weightsList=weightsA,
                                              extraLists=extrasA,
                                              customChrLength=customChrLength)

        track2 = createSimpleTestTrackContent(startList=startsB,
                                              endList=endsB, valList=valsB,
                                              strandList=strandsB,
                                              idList=idsB, edgeList=edgesB,
                                              weightsList=weightsB,
                                              extraLists=extrasB,
                                              customChrLength=customChrLength)

        s = Subtract(track1, track2, resultAllowOverlap=resultAllowOverlap,
                     useStrands=useStrands,
                     treatMissingAsNegative=treatMissingAsNegative,
                     debug=debug)

        tc = s.calculate()

        resFound = False

        for (k, v) in tc.getTrackViews().items():
            if cmp(k, self.chr1) == 0:
                # All test tracks are in chr1
                newStarts = v.startsAsNumpyArray()
                newEnds = v.endsAsNumpyArray()
                newVals = v.valsAsNumpyArray()
                newStrands = v.strandsAsNumpyArray()
                newIds = v.idsAsNumpyArray()
                newEdges = v.edgesAsNumpyArray()
                newWeights = v.weightsAsNumpyArray()
                newExtras = v.allExtrasAsDictOfNumpyArrays()

                resFound = True

                if expEnds is None:
                    # Assuming a point type track. Creating the expected ends.
                    expEnds = np.array(expStarts) + 1

                if debug:
                    print("**********************")
                    print("DEBUG: Subtract result")
                    print("expTrackFormatType: {}".format(expTrackFormatType))
                    print("newTrackFormatType: {}".format(
                        v.trackFormat.getFormatName()))
                    print("expStarts: {}".format(expStarts))
                    print("newStarts: {}".format(newStarts))
                    print("expEnds: {}".format(expEnds))
                    print("newEnds: {}".format(newEnds))
                    print("expStrands: {}".format(expStrands))
                    print("newStrands: {}".format(newStrands))
                    print("expVals:: {}".format(expVals))
                    print("newVals:: {}".format(newVals))
                    print("expIds: {}".format(expIds))
                    print("newIds: {}".format(newIds))
                    print("expEdges: {}".format(expEdges))
                    print("newEdges: {}".format(newEdges))
                    print("expeights: {}".format(expWeights))
                    print("newWeights: {}".format(newWeights))
                    print("**********************")

                if expTrackFormatType is not None:
                    # Check that the track is of the expected type.
                    self.assertTrue(v.trackFormat.getFormatName() ==
                                    expTrackFormatType)

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

                if expVals is not None:
                    self.assertTrue(newVals is not None)
                    self.assertTrue(np.array_equal(newVals, expVals))
                else:
                    self.assertTrue(newVals is None)

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
                    self.assertTrue(newWeights is not None)
                    self.assertTrue(np.array_equal(newWeights, expWeights))
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
                self.assertEqual(v.startsAsNumpyArray().size, 0)
                self.assertEqual(v.endsAsNumpyArray().size, 0)

        if expNoResult:
            self.assertFalse(resFound)
        else:
            self.assertTrue(resFound)

    # **** Points tests ****

    def testPointsSimple(self):
        """
        Simple points subtract
        :return: None
        """
        self._runTest(startsA=[1,2,3], startsB=[3], expStarts=[1,2],
                      expTrackFormatType="Points")

    def testPointsNoOverlap(self):
        """
        Test subtracting a track without overlap.
        :return:
        """
        self._runTest(startsA=[1,4], startsB=[14], expStarts=[1,4],
                      expTrackFormatType="Points")

    def testPointsAtStart(self):
        self._runTest(startsA=[14,463], startsB=[14,45], expStarts=[463],
                      expTrackFormatType="Points")

    def testPointsAtMiddle (self):
        self._runTest(startsA=[14,36,65], startsB=[24,36,463],
                      expStarts=[14,65], expTrackFormatType="Points")

    # **** Segments tests ****
    def testSegmentsSimple(self):
        """
        Segments intersect, simple.
        Two non overlapping segments
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[4], endsB=[8],
                      expStarts=[2], expEnds=[4],
                      expTrackFormatType="Segments")

    def testSegmentsNoOverlap(self):
        """
        Segment intersect, no overlap
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[6], endsB=[8],
                      expStarts=[2], expEnds=[4],
                      expTrackFormatType="Segments")

    def testSegmentsOverlapABeforeB(self):
        """
        Two partially overlapping segments, A before B
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[3], endsB=[5],
                      expStarts=[2], expEnds=[3],
                      expTrackFormatType="Segments")

    def testSegmentsOverlapBBeforeA(self):
        """
        Two partially overlapping segments, B before A
        :return: None
        """
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[4],
                      expStarts=[4], expEnds=[5],
                      expTrackFormatType="Segments")

    def testSegmentsOverlapBInsideA(self):
        """
        Two overlapping segments, B totally inside A
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[3], endsB=[5],
                      expStarts=[2,5], expEnds=[3,6],
                      expTrackFormatType="Segments")

    def testSegmentsOverlapAInsideB(self):
        """
        Two overlapping segments, A totally inside B
        :return: None
        """
        self._runTest(startsA=[3], endsA=[5], startsB=[2], endsB=[6],
                      expNoResult=True)

    def testSegmentsTotalOverlap(self):
        """
        Two totally overlapping segments, A == B
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[4],
                      expNoResult=True,)

    def testSegmentsOverlapBAtStartOfA(self):
        """
        Two overlapping segments, B totally inside A
        B.start == A.start
        len(A) > len(B)
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[4], expEnds=[6],
                      expTrackFormatType="Segments")

    def testSegmentsOverlapAAtStartOfB(self):
        """
        Two overlaping segments, A totally inside B
        A.start == B.start
        len(B) > len (A)
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[2], endsB=[6],
                      expNoResult=True)

    def testSegmentsOverlapBAtEndOfA(self):
        """
        Two overlapping segments, B totally inside A
        A.end == B.end
        len(A) > len (B)
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], startsB=[4], endsB=[6],
                      expStarts=[2], expEnds=[4],
                      expTrackFormatType="Segments")

    def testSegmentsOverlapAAtEndOfB(self):
        """
        Two overlapping segments, A totally inside B
        B.end == A.end
        len(B) > len (A)
        :return: None
        """
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[6],
                      expNoResult=True)

    def testSegmentsTouchingABeforeB(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start

        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], startsB=[4], endsB=[6],
                      expStarts=[2],expEnds=[4], expTrackFormatType="Segments")

    def testSegmentsTouchingBBeforeA(self):
        """
        Two none overlapping "touching" segments
        A.end == B.start

        :return: None
        """
        self._runTest(startsA=[4], endsA=[6], startsB=[2], endsB=[4],
                      expStarts=[4], expEnds=[6],
                      expTrackFormatType="Segments")

    def testSegmentsBCoversMultipleInA(self):
        """
        B covers multiple segments in A
        :return: None
        """
        self._runTest(startsA=[2, 6], endsA=[4, 8], startsB=[3], endsB=[7],
                      expStarts=[2,7], expEnds=[3, 8],
                      expTrackFormatType="Segments")

    def testSegmentsBCoversMultipleInAComplex(self):
        """
        A covers multiple segments in B
        :return: None
        """
        self._runTest(startsA=[2], endsA=[15], startsB=[3,7], endsB=[5,10],
                      expStarts=[2,5,10], expEnds=[3,7,15],
                      expTrackFormatType="Segments")

    # *** Segments with index ***
    # In these test we check that the index return corresponds with the
    # correct index from track A
    def testIndexSegmentsOverlapABeforeB(self):
        """
        Test if the index is correct
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], valsA=[10], startsB=[4],
                      endsB=[8], expStarts=[2], expEnds=[4], expVals=[10],
                      expTrackFormatType="Valued segments")

    def testIndexSegmentsOverlapBBeforeA(self):
        """
        Test if the index is correct
        :return: None
        """
        self._runTest(startsA=[6], endsA=[10], valsA=[10], startsB=[4],
                      endsB=[8], expStarts=[8], expEnds=[10], expVals=[10],
                      expTrackFormatType="Valued segments")

    def testIndexSegmentsNoOverlap(self):
        """
        Segment intersect, no overlap
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], valsA=[10], startsB=[6],
                      endsB=[8], expStarts=[2], expEnds=[4], expVals=[10],
                      expTrackFormatType="Valued segments")

    def testIndexSegmentsOverlapMultipleBInsideA(self):
        """
        Two partially overlapping segments, A before B
        :return: None
        """
        self._runTest(startsA=[2], endsA=[15], valsA=[10], startsB=[3,8,12],
                      endsB=[5,10,13], expStarts=[2,5,10,13],
                      expEnds=[3,8,12,15], expVals=[10,10,10,10],
                      expTrackFormatType="Valued segments")

    # *** Strands, only extract ***
    # We do not follow the strands, just testing that the strand info from
    # track A is kept.
    def testStrandsNotUsedStart(self):
        """
        Test if the index is correct
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], strandsA=['+'], startsB=[4],
                      endsB=[8], expStarts=[2], expEnds=[4], expStrands=['+'],
                      expTrackFormatType="Segments")

    def testStrandNotUsedEnd(self):
        """
        Test if the index is correct
        :return: None
        """
        self._runTest(startsA=[6], endsA=[10], strandsA=['-'], startsB=[4],
                      endsB=[8], expStarts=[8], expEnds=[10], expStrands=['-'],
                      expTrackFormatType="Segments")

    def testStrandsNotUsedNoOverlap(self):
        """
        Segment intersect, no overlap
        :return: None
        """
        self._runTest(startsA=[2], endsA=[4], strandsA=['.'], startsB=[6],
                      endsB=[8], expStarts=[2], expEnds=[4], expStrands=['.'],
                      expTrackFormatType="Segments")

    def testStrandsNotUsedMultipleOverlap(self):
        """
        Two overlapping segments inside A
        :return:
        """
        self._runTest(startsA=[2], endsA=[15], strandsA=['+'],
                      startsB=[3,8,12], endsB=[5,10,13], expStarts=[2,5,10,13],
                      expEnds=[3,8,12,15], expStrands=['+','+','+','+'],
                      expTrackFormatType="Segments")

    # *** Strands, follow direction ***
    # Test that we only subtract elements with the same strand
    def testUseStrandsOnlyPositive(self):
        """
        Test if the index is correct
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], strandsA=['+'], startsB=[4],
                      endsB=[8], strandsB=['+'], expStarts=[2], expEnds=[4],
                      expStrands=['+'], useStrands=True,
                      treatMissingAsNegative=False,
                      expTrackFormatType="Segments")

    def testUseStrandsOnlyNegative(self):
        """
        Test if the index is correct
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], strandsA=['-'], startsB=[4],
                      endsB=[8], strandsB=['-'], expStarts=[2], expEnds=[4],
                      expStrands=['-'], useStrands=True,
                      treatMissingAsNegative=False,
                      expTrackFormatType="Segments")

    def testUseStrandsOnlyMissingDefault(self):
        """
        Test missing, default
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], strandsA=['.'], startsB=[4],
                      endsB=[8], strandsB=['+'], expStarts=[2], expEnds=[4],
                      expStrands=['.'], useStrands=True,
                      treatMissingAsNegative=False,
                      expTrackFormatType="Segments")

    def testUseStrandsOnlyMissingDefaultNoSubtract(self):
        """
        Test missing, default
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], strandsA=['.'], startsB=[4],
                      endsB=[8], strandsB=['-'], expStarts=[2], expEnds=[6],
                      expStrands=['.'], useStrands=True,
                      treatMissingAsNegative=False,
                      expTrackFormatType="Segments")

    def testUseStrandsOnlyMissingAsNegative(self):
        """
        Test missing, default
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], strandsA=['.'], startsB=[4],
                      endsB=[8], strandsB=['-'], expStarts=[2], expEnds=[4],
                      expStrands=['.'], useStrands=True,
                      treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testUseStrandsOnlyMissingAsNegativeNoOverlap(self):
        """
        Test missing, default
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], strandsA=['.'], startsB=[4],
                      endsB=[8], strandsB=['+'], expStarts=[2], expEnds=[6],
                      expStrands=['.'], useStrands=True,
                      treatMissingAsNegative=True,
                      expTrackFormatType="Segments")

    def testUseStrandsPositiveNegative(self):
        """
        We expect to se no subtracktion
        :return: None
        """
        self._runTest(startsA=[2], endsA=[6], strandsA=['+'], startsB=[4],
                      endsB=[8], strandsB=['-'], expStarts=[2], expEnds=[6],
                      expStrands=['+'], useStrands=True,
                      treatMissingAsNegative=False,
                      expTrackFormatType="Segments")

    def testUseStrandsMix(self):
        """
        Test with both
        :return:
        """
        self._runTest(startsA=[5,20], endsA=[10,26], strandsA=['+','-'],
                      startsB=[6,22], endsB=[8,24], strandsB=['+', '-'],
                      expStarts=[5,8,20,24], expEnds=[6,10,22,26],
                      expStrands=['+','+','-','-'], useStrands=True,
                      treatMissingAsNegative=False,
                      expTrackFormatType="Segments", debug=True)

    def testUseStrandsMixSorting(self):
        """
        Test that the new track is sorted correctly
        :return:
        """
        self._runTest(startsA=[5,20], endsA=[10,26], strandsA=['-','+'],
                      startsB=[6,22], endsB=[8,24], strandsB=['-', '+'],
                      expStarts=[5,8,20,24], expEnds=[6,10,22,26],
                      expStrands=['-','-','+','+'], useStrands=True,
                      treatMissingAsNegative=False,
                      expTrackFormatType="Segments", debug=True)

    # **** Points - Segments ****
    def testPointsAndSegments(self):
        self._runTest(startsA=[1,2,3,4], startsB=[3], endsB=[10],
                      expStarts=[1,2], expTrackFormatType="Points")

    def testPointsAndSegmentsTotal(self):
        self._runTest(startsA=[3,4,8], startsB=[3], endsB=[10],
                      expNoResult=True, expTrackFormatType="Points")

    # **** Segments - Points ****
    def testSegmentsAndPoints(self):
        self._runTest(startsA=[3], endsA=[10], startsB=[4,12],
                      expStarts=[3,5], expEnds=[4,10],
                      expTrackFormatType="Segments")

    # *** Test track input ***
    # Test that the different information is saved into the new track
    def testInputValuedPoints(self):
        """
        Test that the values are kept.
        :return:
        """
        self._runTest(startsA=[10,15], valsA=[100,200], startsB=[12],
                      endsB=[20], expStarts=[10], expVals=[100],
                      expTrackFormatType="Valued points")

    def testInputLinkedPoints(self):
        """
        Test linked points as input
        :return:
        """
        self._runTest(startsA=[10,15], idsA=['1','2'], edgesA=['1','2'],
                      startsB=[12], endsB=[20], expStarts=[10], expIds=['1'],
                      expEdges=['1'], expTrackFormatType="Linked points")

    def testInputLinkedValuedPoints(self):
        """
        Test linked valued points as input
        :return:
        """
        self._runTest(startsA=[10,15], idsA=['1','2'], edgesA=['1','2'],
                      valsA=[100,200], startsB=[12], endsB=[20],
                      expStarts=[10], expVals=[100],
                      expIds=['1'], expEdges=['1'],
                      expTrackFormatType="Linked valued points")

    def testInputValuedSegments(self):
        """
        Test Valued segments as input
        :return:
        """
        self._runTest(startsA=[10], endsA=[20], valsA=[100],
                      startsB=[15], endsB=[40], expStarts=[10],
                      expEnds=[15], expVals=[100],
                      expTrackFormatType="Valued segments",)

    def testInputLinkedSegments(self):
        """
        Test Linked segments as input
        :return:
        """
        self._runTest(startsA=[10], endsA=[20], idsA=['1'], edgesA=['1'],
                      startsB=[15], endsB=[40], expStarts=[10],
                      expEnds=[15], expIds=['1'], expEdges=['1'],
                      expTrackFormatType="Linked segments")

    def testInputLinkedValuedSegments(self):
        """
        Test Linked valued segments as inpout
        :return:
        """
        self._runTest(startsA=[10], endsA=[20], valsA=[100], idsA=['1'],
                      edgesA=['1'], startsB=[15], endsB=[40], expStarts=[10],
                      expEnds=[15], expVals=[100], expIds=['1'],
                      expEdges=['1'],
                      expTrackFormatType="Linked valued segments")

if __name__ == "__main__":
    unittest.main()
