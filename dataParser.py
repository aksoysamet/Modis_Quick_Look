import numpy as np


class DataParser:
    def getHeader(self, byte):
        groupSequence = (byte[2] & 0xC0) >> 6
        dayCount = ((byte[6] & 0xFF) << 8) | (byte[7] & 0xFF)
        coarseTime = ((byte[8] & 0xFF) << 24) | ((byte[9] & 0xFF) << 16) | ((byte[10] & 0xFF) << 8) | (byte[11] & 0xFF)  # noqa
        timeTag = ((dayCount - 4383) * 86400 * 1000) + coarseTime
        packet_type = (byte[14] & 0x70) >> 4
        mirrorSide = (byte[14] & 0x01)
        scanCount = (byte[14] & 0x0E) >> 1
        sid = (byte[15] & 0x80) >> 7
        sample_count = ((byte[15] & 0x7F) << 4) | ((byte[16] & 0xF0) >> 4)
        return (groupSequence, timeTag, packet_type, mirrorSide, scanCount, sid, sample_count)  # noqa

    def read_uint12(self, data_chunk, offset=18):
        data = np.frombuffer(data_chunk, dtype=np.uint8, offset=offset)
        fst_uint8, mid_uint8, lst_uint8 = np.reshape(data, (data.shape[0] // 3, 3)).astype(np.uint16).T  # noqa
        fst_uint12 = (fst_uint8 << 4) + (mid_uint8 >> 4)
        snd_uint12 = ((mid_uint8 % 16) << 8) + lst_uint8
        return np.reshape(np.concatenate((fst_uint12[:, None], snd_uint12[:, None]), axis=1), 2 * fst_uint12.shape[0])  # noqa
