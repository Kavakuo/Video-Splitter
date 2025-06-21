class SplitPoint(object):
    def __init__(self, time: str, title: str):
        self._time = time
        self._title = title

    @property
    def time(self):
        return self._time
    
    @property
    def title(self):
        return self._title

class VideoFile(object):
    def __init__(self, path: str, syncTimestamp: str):
        self._path = path
        self._syncTimestamp = syncTimestamp

    @property
    def path(self):
        return self._path
    
    @property
    def syncTimestamp(self):
        return self._syncTimestamp
