
import sys
import os
import numpy as np
import logging

from collections import OrderedDict
from cStringIO import StringIO

from gtrackcore.core.Api import importFile
from gtrackcore.core.Api import _trackNameExists
from gtrackcore.core.Api import listAvailableGenomes
from gtrackcore.core.Api import listAvailableTracks

from gtrackcore.track.core.Track import Track
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat
from gtrackcore.track.core.TrackView import TrackView

from gtrackcore.track_operations.TrackContents import TrackContents

# *** Gtrackcore API ***

def isTrackInGtrack(genome, trackName):
    """
    Add this functionality to API..
    """

    with Capturing() as output:
        listAvailableTracks(genome)

    for i in output:
        if trackName in i:
            return True
    return False

def importTrackIntoGTrack(trackName, genome, path):
    """
    Load a gtrack tabular file into GTrackCore.

    :param trackName:
    :param genome:
    :param path:
    :return:
    """

    if not isTrackInGtrack(genome.name, trackName):
        print("not in gtrack")
        importFile(path, genome.name, trackName)
    else:
        print("in gtrack")

# *** Track handling ***

def printTrackView(tv):
    """
    Print the contents of a trackView
    :param tv:
    :return:
    """

    output = OrderedDict()

    starts = tv.getStartsAsNumpyArray()
    ends = tv.getEndsAsNUmpyArray()

    output['starts'] = starts
    output['ends'] = ends

    vals = tv.getValsAsNumpyArray()
    strands = tv.getStrandsAsNumpyArray()
    ids = tv.getIdsAsNumpyArray()
    edges = tv.getEdgesAsNumpyArray()
    weights = tv.getWeightsAsNympyArray()

    if vals != None and len(vals) > 0:
        output['vals'] = vals

    if strands != None and len(starts) > 0:
        output['strands'] = strands

    if ids != None and len(ids) > 0:
        output['ids'] = ids

    if edges != None and len(edges) > 0:
        output['edges'] = edges

    if weights != None and len(edges) > 0:
        output['weights'] = weights


def createRawResultTrackView(index, region, baseTrack, allowOverlap,
                             newStarts=None, newEnds=None, newStrands=None,
                             newValues=None, encoding=None):
    """

    TODO: Expand to support more track types.

    Used by operations of create a TrackView out of the result of the raw
    operation.

    This method may not be suitable for all Raw operations.

    When calculating a new track using a raw operation we sometimes want to
    keep other information than the start, ends. To make this easier we
    return the starts, end and an index corresponding to where in track A
    these values are stored.

    This method finds these values if they are defined in track A and
    returns a new TrackView object.

    :param starts: Numpy array. Starts of the new track.
    :param ends: Numpy array. Ends of the new track.
    :param index: Numpy array. Index in track A corresponding track segment
    in the result
    :param region: Genomic region of the trackView
    :param baseTrack: trackViews. Track used as basis
    :return: TrackView.
    """

    logging.debug("Creating new raw result track view")

    if newStarts is not None and newEnds is not None:
        print("***F****")
        print(newStarts)
        print(newEnds)
        print("***F****")

        assert len(newStarts) == len(newEnds)

    if index is None:
        # Expand this co use what we have..
        if newStarts is None or newEnds is None:
            raise NotImplementedError
        tv = TrackView(region, newStarts, newEnds, None, None, None,
                   None, None, borderHandling='crop',
                   allowOverlaps=allowOverlap)
        return tv

    starts = None
    ends = None
    vals = None
    strands = None
    ids = None
    edges = None
    weights = None

    if encoding is not None:
        nrBaseTracks = len(baseTrack)

        assert nrBaseTracks > 1
        assert isinstance(baseTrack, list)

        # index in the base track
        ind = [None] * nrBaseTracks

        # Indexes in the new track
        enc = [None] * nrBaseTracks
        for i in range(1, nrBaseTracks+1):
            t = np.where(encoding == i)

            enc[i-1] = t
            ind[i-1] = index[t]

        startsBase = [None] * nrBaseTracks
        endsBase = [None] * nrBaseTracks
        valsBase = [None] * nrBaseTracks
        strandsBase = [None] * nrBaseTracks
        idsBase = [None] * nrBaseTracks
        edgesBase = [None] * nrBaseTracks
        weightsBase = [None] * nrBaseTracks
        #extrasBase = [None] * nrBaseTracks
        # Add the extra..

        # Get all of the numpy arrays from the tracks
        for i, track in enumerate(baseTrack):
            startsBase[i] = track.startsAsNumpyArray()
            endsBase[i] = track.endsAsNumpyArray()
            valsBase[i] = track.valsAsNumpyArray()
            strandsBase[i] = track.strandsAsNumpyArray()
            idsBase[i] = track.idsAsNumpyArray()
            edgesBase[i] = track.edgesAsNumpyArray()
            weightsBase[i] = track.weightsAsNumpyArray()

        # If one of the base track is missing a base we ignore it for the
        # rest of the base tracks.
        # This should possible be extended to save the data we have.
        if not all(s is not None for s in startsBase):
            startsBase = None
        if not all(e is not None for e in endsBase):
            endsBase = None
        if not all(v is not None for v in valsBase):
            valsBase = None
        if not all(s is not None for s in strandsBase):
            strandsBase = None
        if not all(i is not None for i in idsBase):
            idsBase = None
        if not all(e is not None for e in edgesBase):
            edgesBase = None
        if not all(w is not None for w in weightsBase):
            weightsBase = None

        if newStarts is not None:
            starts = newStarts
        else:
            if startsBase is None:
                starts = None
            else:
                starts = np.zeros(len(index))
                for i in range(0, nrBaseTracks):
                    starts[enc[i]] = startsBase[i][ind[i]]

        if newEnds is not None:
            ends = newEnds
        else:
            if endsBase is None:
                ends = None
            else:
                ends = np.zeros(len(index))
                for i in range(0, nrBaseTracks):
                    ends[enc[i]] = endsBase[i][ind[i]]

        if newValues is not None:
            # If the operation has created new values we use them instead.
            vals = newValues
        else:
            print("In set vals!")
            if valsBase is None:
                vals = None
            else:
                vals = np.zeros(len(index))
                for i in range(0, nrBaseTracks):
                    vals[enc[i]] = valsBase[i][ind[i]]

            print("After val set")
            print(vals)

        if newStrands is not None:
            # Use the new/updated strands if we have them.
            # with different strand?
            assert len(newStrands) == len(starts)
            strands = newStrands
        else:
            if strandsBase is None:
                strands = None
            else:
                strands = np.zeros(len(index))
                for i in range(0, nrBaseTracks):
                    strands[enc[i]] = strandsBase[i][ind[i]]

        if idsBase is None:
            ids = None
        else:
            ids = np.chararray(len(index))
            for i in range(0, nrBaseTracks):
                ids[enc[i]] = idsBase[i][ind[i]]

        if edgesBase is None:
            edges = None
        else:
            edges = np.zeros(len(index), dtype=object)
            for i in range(0, nrBaseTracks):
                print(edgesBase[i].dtype)
                print(edgesBase[i].shape)
                edges[enc[i]] = edgesBase[i][ind[i]]

            print("***FDSF***")
            print(edges)
            print("***FDSF***")

        if weightsBase is None:
            weights = None
        else:
            weights = np.zeros(len(index))
            for i in range(0, nrBaseTracks):
                weights[enc[i]] = weightsBase[i][ind[i]]
    else:
        print("One base track!")
        if newStarts is not None:
            print("New starts given!")
            starts = newStarts
        else:
            s = baseTrack.startsAsNumpyArray()
            if s is not None:
                starts = s[index]

        if newEnds is not None:
            ends = newEnds
        else:
            e = baseTrack.endsAsNumpyArray()
            if e is not None:
                ends = e[index]

        if newValues is not None:
            # If the operation has created new values we use them instead.
            vals = newValues
        else:
            v = baseTrack.valsAsNumpyArray()
            if v is not None:
                vals = v[index]

        if newStrands is not None:
            # Use the new/updated strands if we have them.
            # with different strand?
            assert len(newStrands) == len(starts)
            strands = newStrands
        else:
            s = baseTrack.strandsAsNumpyArray()
            if s is not None:
                strands = s[index]

        i = baseTrack.idsAsNumpyArray()
        if i is not None:
            ids = i[index]

        e = baseTrack.edgesAsNumpyArray()
        if e is not None:
            edges = e[index]

        w = baseTrack.weightsAsNumpyArray()
        if w is not None:
            weights = w[index]

    # TODO fix extra

    print("$$$$$$$BEFORE$$$$$$$$")
    print("starts: {}".format(starts))
    print("ends: {}".format(ends))
    print("vals: {}".format(vals))
    print("ids: {}".format(ids))
    tv = TrackView(region, starts, ends, vals, strands, ids, edges, weights,
                   borderHandling='crop', allowOverlaps=allowOverlap)
    print("$$$$$$$AFTER$$$$$$$$")
    print("vals: {}".format(tv.valsAsNumpyArray()))
    print("ids: {}".format(tv.idsAsNumpyArray()))
    print("$$$$$$$END$$$$$$$$")

    return tv

def createTrackContentFromFile(genome, path, allowOverlaps):

    #trackName = trackName.split(':')
    # NOT SYSTEM safe!! Fix this later!
    trackName = path.split('/')[-1]
    trackName = trackName.split('.')[0]

    importTrackIntoGTrack(trackName, genome, path)

    track = Track(trackName.split(':'))
    track.addFormatReq(TrackFormatReq(allowOverlaps=False,
                                      borderHandling='crop'))
    trackViewList = OrderedDict()

    for region in genome.regions:

        try:
            trackViewList[region] = track.getTrackView(region)
        except OSError:
            # There can be regions that the track does not cover..
            # This is a temp fix.. should be bare of the api
            pass

    return TrackContents(genome, trackViewList)

def createTrackContentFromTrack(track, genome):
    trackViewList = OrderedDict()

    for region in genome.regions:
        try:
            trackViewList[region] = track.getTrackView(region)
        except OSError:
            # There can be regions that the track does not cover..
            # This is a temp fix.. should be bare of the api
            pass
    return TrackContents(genome, trackViewList)


class Capturing(list):
    """
    Class used to capture the print output from the API. This should be
    fixed by adding more functionality to the API.

    From stackoverflow #16571150
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout
