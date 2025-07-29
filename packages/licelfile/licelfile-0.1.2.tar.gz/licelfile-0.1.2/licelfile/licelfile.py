from typing import Dict, IO, List, Optional
from dataclasses import dataclass, field
import zipfile
from datetime import datetime
import struct
import numpy as np

BYTES_PER_LINE = 80
    
@dataclass
class LicelProfile:
    isActive: bool
    isPhoton: bool
    laserType: int
    nDataPoints: int
    highVoltage: int
    binWidth: float
    wavelength: float
    polarization: str
    binShift: int
    decBinShift: int
    adcBits: int
    nShots: int
    discrLevel: float
    deviceID: str
    nCrate: int
    data: List[float] = field(default_factory=list)
    Reserved: Optional[List[int]] = field(default_factory=list)


@dataclass
class LicelFile:
    """ Единичный файл измерения """
    measurementSite: str = field(default_factory=str)
    altitude: float = field(default_factory=float)
    longitude: float = field(default=131.9)
    latitude: float = field(default=43.1)
    zenith: float = field(default=50)
    laser1NShots: int = field(default=0)
    laser1Freq: int = field(default=0)
    laser2NShots: int = field(default=0)
    laser2Freq: int = field(default=0)
    nDatasets: int = field(default=0)
    laser3NShots: int = field(default=0)
    laser3Freq: int = field(default=0)
    measurementStartTime: datetime = field(default_factory=datetime.now)
    measurementStopTime: datetime  = field(default_factory=datetime.now)
    profiles: List[LicelProfile] = field(default_factory=list)
        

    def _readHeader(self, f:IO[bytes]) -> None:
        h1 = f.read(BYTES_PER_LINE).strip().split()
        h2 = f.read(BYTES_PER_LINE).strip().split()
        h3 = f.read(BYTES_PER_LINE).strip().split()

        # parse second line
        self.measurementSite = h2[0].decode('utf8')
        datetimeTmp = h2[1].decode('utf8')+' '+h2[2].decode('utf8')
        self.measurementStartTime = datetime.strptime(datetimeTmp, '%d/%m/%Y %H:%M:%S')
        datetimeTmp = h2[3].decode('utf8')+' '+h2[4].decode('utf8')
        self.measurementStopTime = datetime.strptime(datetimeTmp, '%d/%m/%Y %H:%M:%S')
        self.altitude = int(h2[5])
        self.longitude = float(h2[6])
        self.latitude = float(h2[7])
        self.zenith = float(h2[8])

        #parse third line
        #  0005001 0020 0000000 0010 12 0000000 0010
        self.laser1NShots = int(h3[0])
        self.laser1Freq = int(h3[1])
        self.laser2NShots = int(h3[2])
        self.laser2Freq = int(h3[3])
        self.nDatasets = int(h3[4])
        self.laser3NShots = int(h3[5])
        self.laser3Freq = int(h3[6])
        
    def _readDatasets(self, f:IO[bytes]) -> None:
        for i in range(self.nDatasets):
            
            line = f.readline().strip().split()
            isActive = bool(int(line[0]))
            isPhoton = bool(int(line[1]))
            laserType = int(line[2])
            nDataPoints=int(line[3])
            laserPol = int(line[4])
            highVoltage = int(line[5])
            binWidth = float(line[6])
            wavepol = line[7].split(b'.')
            wavelength = float(wavepol[0])
            polarization = wavepol[1].decode('utf8')
            binShift = int(line[10])
            decBinShift = int(line[11])
            adcBits = int(line[12])
            nShots = int(line[13])
            discrLevel = float(line[14])
            deviceID = line[15][:2].decode('utf8')
            nCrate = int(line[15][2:])
            profile = LicelProfile(isActive, isPhoton, laserType, nDataPoints,
                                   highVoltage, binWidth, wavelength, polarization, binShift,
                                   decBinShift, adcBits, nShots, discrLevel, deviceID, nCrate)
            self.profiles.append(profile)
        f.read(2)   
        

    def _readData(self, f:IO[bytes]) -> None:
        self._readHeader(f)
        self._readDatasets(f)
        self._readProfile(f)
        pass

    def _readProfile(self, f:IO[bytes]) -> None:
        for i in range(len(self.profiles)):
            nDataPoints = self.profiles[i].nDataPoints*4+2
            data = f.read(nDataPoints)[:-2]
            int32data = list(struct.unpack('<{}l'.format(len(data)//4), data))
            self.profiles[i].data = int32data


def load_licel_file(file_or_path: str|IO[bytes]) -> LicelFile:
    if isinstance(file_or_path, str):
        with open(file_or_path, 'rb') as fin:
            licel_file = LicelFile()
            licel_file._readData(fin)
            
    else:
        licel_file = LicelFile()
        licel_file._readData(file_or_path)
    return licel_file


@dataclass
class LicelFilePack:
    
    files: Dict[str, LicelFile] = field(default_factory=dict)
    

def load_licelfile_pack(zipfname: str) ->LicelFilePack:
    ret:Dict[str, LicelFile] = dict()
        
    # Читаем зип
    with zipfile.ZipFile(zipfname, 'r') as zip_ref:
        for fileinfo in zip_ref.infolist():
            # выбираем фалы измерений
            if fileinfo.filename.startswith('b'):
                try:
                    # открываем и читаем их
                    with zip_ref.open(fileinfo.filename) as file_in_zip:
                        licelFile = load_licel_file(file_in_zip)
                        ret[fileinfo.filename] = licelFile
                except Exception as ex:
                    print(f"Ошибка при обработке файла {fileinfo.filename}: {ex}")

    return LicelFilePack(files=ret)
   
