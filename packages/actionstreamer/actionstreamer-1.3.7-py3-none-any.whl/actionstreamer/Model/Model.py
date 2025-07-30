from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from typing import Optional


class EventStatus(Enum):

    Checked_out = 2
    Complete = 4
    Error = 5
    Pending = 1
    Processing = 3
    Timed_out = 6


class VideoClipStatus(Enum):

    Announced = 1
    Transferring = 2
    Encoding = 3
    FileAvailable = 4
    AnnouncedButMissing = 5
    Highlighted = 6


class VideoClipType(Enum):

    Original_clip = 1
    Concatenated_clip = 2
    Extracted_clip = 3


class AgentType(Enum):

    Video = 1
    View = 2
    Player = 3
    Transcode = 4
    Transfer = 5
    Follower = 6
    Announcer = 7
    AnnounceClip = 8
    UploadFileList = 9
    TestAgent = 7
    Device = 8
    Health = 9
    

class EventType:

    class Video(Enum):
        Start_bars = 9
        Follow = 8
        Start_receive_ActionSync = 5
        Start_recording = 1
        Start_send_ActionSync = 3
        Stop_bars = 10
        Stop_receive_ActionSync = 6
        Stop_recording = 2
        Stop_send_ActionSync = 4
        Test_event = 7
        Test_stop = 11
        Start_RTMP = 14
        Stop_RTMP = 15
        Join_conference = 24
        Leave_conference = 25
        Start_camera_multiplex = 28
        Multiplex_start_recording = 29
        Multiplex_start_send_ActionSync = 30
        Multiplex_join_conference = 31
        Multiplex_start_RTMP = 32
        Start_receive_ActionSync_multiplex = 34
        Multiplex_capture_frames = 36
        Multiplex_stop_recording = 37
        Multiplex_stop_RTMP = 38
        Multiplex_leave_conference = 39
        Multiplex_stop_capturing_frames = 40
        Multiplex_stop_send_ActionSync = 41


    class Transcoding(Enum):
        Transcode_file = 12
        Concatenate_files = 16
        Extract_video = 23
        Concatenate_files_ext = 26

    class Transfer(Enum):
        Transfer_file = 13

    class Device(Enum):  
        Add_network = 17
        Remove_network = 18
        Update_networks = 19
        Send_network_list = 20
        Update_software = 21
        Update_setting = 22
        Clear_flag_queue = 27
        End_process = 35
        Reboot = 42

    class Workflow:
        Event_preset_workflow = 33


class Event:

    def __init__(self, key: int, userID: int, deviceID: int, agentTypeID: int, agentID: int, eventTypeID: int, serverEvent: int, eventStatus: str, eventParameters: str, processID: int, result: str, percentComplete: int, priority: int, expirationEpoch: int, attemptNumber: int, maxAttempts: int, checkoutToken: str, tagString: str, tagNumber: int, creationDate: str, createdBy: int, lastModifiedDate: str, lastModifiedBy: int, **kwargs):
        self.eventID = key
        self.userID = userID
        self.deviceID = deviceID
        self.agentTypeID = agentTypeID
        self.agentID = agentID
        self.eventTypeID = eventTypeID
        self.serverEvent = serverEvent
        self.eventStatus = eventStatus
        self.eventParameters = eventParameters
        self.processID = processID
        self.result = result
        self.percentComplete = percentComplete
        self.priority = priority
        self.expirationEpoch = expirationEpoch
        self.attemptNumber = attemptNumber
        self.maxAttempts = maxAttempts
        self.checkoutToken = checkoutToken
        self.tagString = tagString
        self.tagNumber = tagNumber
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class EventWithNames(Event):

    def __init__(self, key: int, userID: int, deviceID: int, agentTypeID: int, agentID: int, eventTypeID: int, serverEvent: int, eventStatus: int, eventParameters: str, processID: int, result: str, percentComplete: int, priority: int, expirationEpoch: int, attemptNumber: int, maxAttempts: int, checkoutToken: str, tagString: str, tagNumber: int, creationDate: str, createdBy: int, lastModifiedDate: str, lastModifiedBy: int, deviceName: str, eventType: str, agentType: str, version: str, eventStatusName: str, eventStatusDescription: str, agentIndex: int, **kwargs):
        super().__init__(key, userID, deviceID, agentTypeID, agentID, eventTypeID, serverEvent, eventStatus, eventParameters, processID, result, percentComplete, priority, expirationEpoch, attemptNumber, maxAttempts, checkoutToken, tagString, tagNumber, creationDate, createdBy, lastModifiedDate, lastModifiedBy, **kwargs)
        self.deviceName = deviceName
        self.eventType = eventType
        self.agentType = agentType
        self.version = version
        self.eventStatusName = eventStatusName
        self.eventStatusDescription = eventStatusDescription
        self.agentIndex = agentIndex


# Deprecated
class RecordingParameters:

    def __init__(self, height: int = 1920, width: int = 1080, fps: float = 30, bitrate: int = 5000000, vflip: int = 0, hflip: int = 0, encoding: str = '', segmentLengthSeconds: float = 0, audio: int = 0, rotationDegrees: int = 0, **kwargs):
        self.height = height
        self.width = width
        self.fps = fps
        self.bitrate = bitrate
        self.vflip = vflip
        self.hflip = hflip
        self.encoding = encoding
        self.segmentLengthSeconds = segmentLengthSeconds
        self.audio = audio
        #self.rotationDegrees = rotationDegrees
        # Store or ignore unknown fields
        self.extra_fields = kwargs  # Optionally, store unknown fields for debugging or logging

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class RecordingArgs:

    def __init__(self, height: int = 1920, width: int = 1080, fps: float = 30, bitrate: int = 5000000, vflip: int = 0, hflip: int = 0, encoding: str = '', segmentLengthSeconds: float = 0, audio: int = 0, rotationDegrees: int = 0, video_gop_size: int = 60, video_bitrate_mode: int = 0, sequence_header_mode: int = 1, repeat_sequence_header: int = 0, h264_i_frame_period: int = 60, h264_level: int = 11, h264_profile: int = 4, h264_i_qp: int = 20, h264_p_qp: int = 23, h264_b_qp: int = 25, h264_minimum_qp_value: int = 20, h264_maximum_qp_value: int = 51, **kwargs):
        self.height = height
        self.width = width
        self.fps = fps
        self.bitrate = bitrate
        self.vflip = vflip
        self.hflip = hflip
        self.encoding = encoding
        self.segmentLengthSeconds = segmentLengthSeconds
        self.audio = audio
        self.rotationDegrees = rotationDegrees
        self.video_gop_size = video_gop_size
        self.video_bitrate_mode = video_bitrate_mode
        self.sequence_header_mode = sequence_header_mode
        self.repeat_sequence_header = repeat_sequence_header
        self.h264_minimum_qp_value = h264_minimum_qp_value
        self.h264_maximum_qp_value = h264_maximum_qp_value
        self.h264_i_frame_period = h264_i_frame_period
        self.h264_i_qp = h264_i_qp
        self.h264_p_qp = h264_p_qp
        self.h264_b_qp = h264_b_qp
        self.h264_level = h264_level
        self.h264_profile = h264_profile

        # Store or ignore unknown fields
        self.extra_fields = kwargs  # Optionally, store unknown fields for debugging or logging

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")

    def to_dict(self):
        """Return a dictionary representation excluding extra_fields."""
        filtered_parameters = {}

        for attribute_name, attribute_value in self.__dict__.items():
            if attribute_name != "extra_fields":
                filtered_parameters[attribute_name] = attribute_value

        return filtered_parameters

    def to_json(self):
        """Return a JSON string representation excluding extra_fields."""
        return json.dumps(self.to_dict())
    

class StopReceiveActionSyncArgs:

    def __init__(self, senderIP: str = '', senderPort: int = 0, **kwargs):
        self.sender_ip = senderIP
        self.sender_port = senderPort
        
        # Store or ignore unknown fields
        self.extra_fields = kwargs  # Optionally, store unknown fields for debugging or logging

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")

    def to_dict(self):
        """Return a dictionary representation excluding extra_fields."""
        filtered_parameters = {}

        for attribute_name, attribute_value in self.__dict__.items():
            if attribute_name != "extra_fields":
                filtered_parameters[attribute_name] = attribute_value

        return filtered_parameters

    def to_json(self):
        """Return a JSON string representation excluding extra_fields."""
        return json.dumps(self.to_dict())
    

class ReceiveActionSyncArgs:

    def __init__(self, bufferMS: int = 200, audio: int = 0, rotationDegrees: int = 0, filename: str = '', deviceIP: str = '', devicePort: int = 0, cardID: int = 0, cardDeviceID: int = 0, senderDeviceID: int = 0, **kwargs):
        self.buffer_ms = bufferMS
        self.audio = audio
        self.rotationDegrees = rotationDegrees
        self.filename = filename
        self.device_ip = deviceIP
        self.device_port = devicePort
        self.card_id = cardID
        self.card_device_id = cardDeviceID
        self.sender_device_id = senderDeviceID
        
        # Store or ignore unknown fields
        self.extra_fields = kwargs  # Optionally, store unknown fields for debugging or logging

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")

    def to_dict(self):
        """Return a dictionary representation excluding extra_fields."""
        filtered_parameters = {}

        for attribute_name, attribute_value in self.__dict__.items():
            if attribute_name != "extra_fields":
                filtered_parameters[attribute_name] = attribute_value

        return filtered_parameters

    def to_json(self):
        """Return a JSON string representation excluding extra_fields."""
        return json.dumps(self.to_dict())
    
class SendActionSyncArgs:

    def __init__(self, width: int = 1280, height: int = 720, audio: int = 0, rotationDegrees: int = 0, serverIP: str = '', port: int = 0, fps: float = 30.0, bitrate: int = 0, **kwargs):
        self.width = width
        self.height = height
        self.audio = audio
        self.rotationDegrees = rotationDegrees
        self.server_ip = serverIP
        self.port = port
        self.fps = fps
        self.bitrate = bitrate

        # Store or ignore unknown fields
        self.extra_fields = kwargs  # Optionally, store unknown fields for debugging or logging

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")

    def to_dict(self):
        """Return a dictionary representation excluding extra_fields."""
        filtered_parameters = {}

        for attribute_name, attribute_value in self.__dict__.items():
            if attribute_name != "extra_fields":
                filtered_parameters[attribute_name] = attribute_value

        return filtered_parameters

    def to_json(self):
        """Return a JSON string representation excluding extra_fields."""
        return json.dumps(self.to_dict())
  

class CameraMultiplexArgs:

    def __init__(self, height: int = 1920, width: int = 1080, fps: float = 30, audio: int = 0, **kwargs):
        self.height = height
        self.width = width
        self.fps = fps
        self.audio = audio

        # Store or ignore unknown fields
        self.extra_fields = kwargs  # Optionally, store unknown fields for debugging or logging

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")

    def to_dict(self):
        """Return a dictionary representation excluding extra_fields."""
        filtered_parameters = {}

        for attribute_name, attribute_value in self.__dict__.items():
            if attribute_name != "extra_fields":
                filtered_parameters[attribute_name] = attribute_value

        return filtered_parameters

    def to_json(self):
        """Return a JSON string representation excluding extra_fields."""
        return json.dumps(self.to_dict())
    

# Deprecated
class RTMPParameters:

    def __init__(self, height: int = 1920, width: int = 1080, fps: float = 30, bitrate: int = 5000000, server: str = '', port: int = 0, streamName: str = '', streamKey: str = '', hflip: int = 0, vflip: int = 0, splitVideoSource: str = '', **kwargs):
        self.height = height
        self.width = width
        self.fps = fps
        self.bitrate = bitrate
        self.server = server
        self.port = port
        self.stream_name = streamName
        self.stream_key = streamKey
        self.hflip = hflip
        self.vflip = vflip
        self.split_video_source = splitVideoSource
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class RTMPArgs:

    def __init__(self, height: int = 1920, width: int = 1080, fps: float = 30, bitrate: int = 5000000, server: str = '', port: int = 0, streamName: str = '', streamKey: str = '', hflip: int = 0, vflip: int = 0, rotationDegrees: int = 0, splitVideoSource: str = '', **kwargs):
        self.height = height
        self.width = width
        self.fps = fps
        self.bitrate = bitrate
        self.server = server
        self.port = port
        self.stream_name = streamName
        self.stream_key = streamKey
        self.hflip = hflip
        self.vflip = vflip
        self.rotationDegrees = rotationDegrees
        self.split_video_source = splitVideoSource
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class File:

    def __init__(self, key: int = 0, userID: int = 0, deviceID: int = 0, filename: str = '', fileGUID: str = '', sHA256Hash: str = '', fileLocation: str = '', fileExpiration: str = '', fileSize: int = '', fileInS3: bool = False, creationDate: str = '', createdBy: int = '', lastModifiedDate: str = '', lastModifiedBy: int = 0, **kwargs):
        self.key = key
        self.userID = userID
        self.deviceID = deviceID
        self.filename = filename
        self.fileGUID = fileGUID
        self.sHA256Hash = sHA256Hash
        self.fileLocation = fileLocation
        self.fileExpiration = fileExpiration
        self.fileSize = fileSize
        self.fileInS3 = fileInS3
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class VideoClip:

    def __init__(self, key: int = 0, userID: int = 0, deviceID: int = 0, fileID: int = 0, tsFileID: int = 0, videoClipTypeID: int = 1, videoClipStatus: int = 0, videoClipParameters: str = '', localFilePath: str = '', height: int = 0, width: int = 0, fileSize: int = 0, framesPerSecond: float = 0, bitrate: int = 0, audioStatus: int = 0, startTime: int = 0, startTimeMs: int = 0, endTime: int = 0, endTimeMs: int = 0, clipLengthInSeconds: float = 0, tagListID: int = 0, creationDate: str = '', createdBy: int = 0, lastModifiedDate: int = '', lastModifiedBy: int = 0, **kwargs):
        self.videoClipID = key
        self.userID = userID
        self.deviceID = deviceID
        self.fileID = fileID
        self.tsFileID = tsFileID
        self.videoClipTypeID = videoClipTypeID
        self.videoClipStatus = videoClipStatus
        self.videoClipParameters = videoClipParameters
        self.localFilePath = localFilePath
        self.height = height
        self.width = width
        self.fileSize = fileSize
        self.framesPerSecond = framesPerSecond
        self.bitrate = bitrate
        self.audioStatus = audioStatus
        self.startTime = startTime
        self.startTimeMs = startTimeMs
        self.endTime = endTime
        self.endTimeMs = endTimeMs
        self.clipLengthInSeconds = clipLengthInSeconds
        self.tagListID = tagListID
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


# Deprecated
class TranscodingParameters:

    def __init__(self, fileID: int, source: str, sourceFile: str, targetFile: str, fps: float, codec: str, splitVideoSource: str = '', **kwargs):
        self.fileID = fileID
        self.source = source
        self.sourceFile = sourceFile
        self.targetFile = targetFile
        self.fps = fps
        self.codec = codec
        self.split_video_source = splitVideoSource
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class TranscodingArgs:

    def __init__(self, fileID: int, source: str, sourceFile: str, targetFile: str, fps: float, codec: str, splitVideoSource: str = '', **kwargs):
        self.fileID = fileID
        self.source = source
        self.sourceFile = sourceFile
        self.targetFile = targetFile
        self.fps = fps
        self.codec = codec
        self.split_video_source = splitVideoSource
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class TransferArgs:

    def __init__(self, fileID: int, videoClipID: int, localFilePath: str, remoteFilename: str, remoteFolderPath: str, url: str, action: str, attemptNumber: int, maxAttempts: int, firstAttemptStartTime: int, maxTimeToTryInSeconds: int, **kwargs):
        self.fileID = fileID
        self.videoClipID = videoClipID
        self.localFilePath = localFilePath
        self.remoteFilename = remoteFilename
        self.remoteFolderPath = remoteFolderPath
        self.url = url,
        self.action = action
        self.attemptNumber = attemptNumber,
        self.maxAttempts = maxAttempts
        self.firstAttemptStartTime = firstAttemptStartTime,
        self.maxTimeToTryInSeconds = maxTimeToTryInSeconds
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class ConcatenateClipsArgs:

    def __init__(self, deviceID: int, deviceName: str, startEpoch: int, endEpoch: int, uploadURL: str, postbackURL: str, videoClips: list[VideoClip], **kwargs):
        self.deviceID = deviceID
        self.deviceName = deviceName
        self.startEpoch = startEpoch
        self.endEpoch = endEpoch
        self.uploadURL = uploadURL
        self.postbackURL = postbackURL
        self.videoClips = videoClips
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class ConferenceArgs:

    def __init__(self, url: str, roomName: str, displayName: str, videoWidth: int = 1280, videoHeight: int = 720, framerate: float = 30, videoBitrate: int = 1000000, sendVideo: bool = True, sendAudio: bool = True, receiveVideo: bool = True, receiveAudio: bool = True, rotationDegrees: int = 0, splitVideoSource: str = '', **kwargs):
        self.url = url
        self.roomName = roomName
        self.displayName = displayName
        self.videoHeight = videoHeight
        self.videoWidth = videoWidth
        self.videoBitrate = videoBitrate
        self.framerate = framerate
        self.sendVideo = sendVideo
        self.sendAudio = sendAudio
        self.receiveVideo = receiveVideo
        self.receiveAudio = receiveAudio
        self.rotationDegrees = rotationDegrees
        self.split_video_source = splitVideoSource
        # Store or ignore unknown fields
        self.extra_fields = kwargs  # Optionally, store unknown fields for debugging or logging

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class EpochRange:

    def __init__(self, startEpoch: int, endEpoch: int, **kwargs):
        self.startEpoch = startEpoch
        self.endEpoch = endEpoch
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class WifiConnection:

    def __init__(self, ssid: str = '', connectionName: str = '', password: str = '', priority: int = 0, **kwargs):
        self.ssid = ssid
        self.password = password
        self.priority = priority
        self.connection_name = connectionName
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")

       
class NameValuePair:

    def __init__(self, name: str, value: str, **kwargs):
        self.name = name
        self.value = value
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class EventDetails:

    def __init__(self, eventID: int = None, eventStatus: int = None, eventParameters: str = None, result: str = None, percentComplete: float = None, priority: int = None, attemptNumber: int = None, maxAttempts: int = None, tagString: str = None, tagNumber: int = None, **kwargs):
        self.eventID = eventID
        self.eventStatus = eventStatus
        self.eventParameters = eventParameters
        self.result = result
        self.percentComplete = percentComplete
        self.priority = priority
        self.attemptNumber = attemptNumber
        self.maxAttempts = maxAttempts
        self.tagString = tagString
        self.tagNumber = tagNumber
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class StandardResult:

    def __init__(self, code: str, description: str, **kwargs):
        self.code = code
        self.description = description
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class DeviceObject:

    def __init__(self, key: int = 0, deviceTypeID: int = 0, userID: int = 0, deviceName: str = '', serialNumber: str = '', deviceDescription: str = '', recentOutput: str = '', cameraStatus: str = '', lastIPAddress: str = '', tunnelIPAddress: str = '', lastHeardFromDate: datetime = datetime.now(), softwareDate: datetime = datetime.now(), location: str = '', setupStatus: int = 0, autoSendFiles: int = 0, runStartupEvent: int = 0, deviceReadyEventPresetID: int = 0, standaloneEventPresetID: int = 0, logHealth: int = 0, runAnalytics: int = 0, audioChannelName: str = '', volume: int = 0, commentListID = 0, isArchived: bool = False, gUID: str = '', creationDate: datetime = datetime.now(), createdBy: int = 0, lastModifiedDate: datetime = datetime.now(), lastModifiedBy: int = 0, **kwargs):
        self.key = key
        self.deviceTypeID = deviceTypeID
        self.userID = userID
        self.deviceName = deviceName
        self.serialNumber = serialNumber
        self.deviceDescription = deviceDescription
        self.recentOutput = recentOutput
        self.cameraStatus = cameraStatus
        self.lastIPAddress = lastIPAddress
        self.tunnelIPAddress = tunnelIPAddress
        self.lastHeardFromDate = lastHeardFromDate
        self.softwareDate = softwareDate
        self.location = location
        self.setupStatus = setupStatus
        self.autoSendFiles = autoSendFiles
        self.runStartupEvent = runStartupEvent
        self.deviceReadyEventPresetID = deviceReadyEventPresetID
        self.standaloneEventPresetID = standaloneEventPresetID
        self.logHealth = logHealth
        self.runAnalytics = runAnalytics
        self.audioChannelName = audioChannelName
        self.volume = volume
        self.commentListID = commentListID
        self.isArchived = isArchived
        self.gUID = gUID
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class VideoClip:

    def __init__(self, key: int = 0, userID: int = 0, deviceID: int = 0, fileID: int = 0, tSFileID: int = 0, videoClipStatus: int = 0, videoClipTypeID: int = 0, videoClipParameters: str = '', localFilePath: str = '', height: int = 0, width: int = 0, filesize: int = 0, framesPerSecond: float = 0, bitrate: int = 0, audioStatus: int = 0, startTime: int = 0, startTimeMs: int = 0, endTime: int = 0, endTimeMs: int = 0, clipLengthInSeconds: float = 0, tagListID: int = 0, creationDate: str = '', createdBy: int = 0, lastModifiedDate: int = '', lastModifiedBy: int = 0, **kwargs):
        self.videoClipID = key
        self.userID = userID
        self.deviceID = deviceID
        self.fileID = fileID
        self.tSFileID = tSFileID
        self.videoClipStatus = videoClipStatus
        self.videoClipTypeID = videoClipTypeID
        self.videoClipParameters = videoClipParameters
        self.localFilePath = localFilePath
        self.height = height
        self.width = width
        self.filesize = filesize
        self.framesPerSecond = framesPerSecond
        self.bitrate = bitrate
        self.audioStatus = audioStatus
        self.startTime = startTime
        self.startTimeMs = startTimeMs
        self.endTime = endTime
        self.endTimeMs = endTimeMs
        self.clipLengthInSeconds = clipLengthInSeconds
        self.tagListID = tagListID
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class CreateVideoClip:

    def __init__(self, deviceID: int = 0, deviceName: str = '', localFilePath: str = '', height: int = 0, width: int = 0, framesPerSecond: float = 0.0, startTime: int = 0, startTimeMs: int = 0, clipLengthInSeconds: float = 0.0, videoClipStatus: int = 0, videoClipTypeID: int = 0, videoClipParameters: str = '', **kwargs):
        self.deviceID = deviceID
        self.deviceName = deviceName
        self.localFilePath = localFilePath
        self.height = height
        self.width = width
        self.framesPerSecond = framesPerSecond
        self.startTime = startTime
        self.startTimeMs = startTimeMs
        self.clipLengthInSeconds = clipLengthInSeconds
        self.videoClipStatus = videoClipStatus
        self.videoClipTypeID = videoClipTypeID
        self.videoClipParameters = videoClipParameters
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class EventPreset:

    def __init__(self, deviceID: int = 0, agentType: str = '', eventType: str = '', eventParameters: str = '', eventPresetName: str = '', priority: int = 1, maxAttempts: int = 5, expirationEpoch: int = 0, **kwargs):
        self.deviceID = deviceID
        self.agentType = agentType
        self.eventType = eventType
        self.eventParameters = eventParameters
        self.eventPresetName = eventPresetName
        self.priority = priority
        self.maxAttempts = maxAttempts
        self.expirationEpoch = expirationEpoch

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")

# Deprecated
class StartRecordingParameters:
# Note 2024-02-14: This is just a duplicate of the above RecordingArgs class
    def __init__(self, width: int = 0, height: int = 0, fps: int = 0, bitrate: int = 0, segmentLengthSeconds: int = 0, hflip: int = 0, vflip: int = 0, rotationDegrees: int = 0, audio: int = 0, splitVideoSource: str = '', **kwargs):
        self.width = width
        self.height = height
        self.fps = fps
        self.bitrate = bitrate
        self.segmentLengthSeconds = segmentLengthSeconds
        self.hflip = hflip
        self.vflip = vflip
        self.rotationDegrees = rotationDegrees
        self.audio = audio
        self.split_video_source = splitVideoSource

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")



class ClearFlagQueueArgs:

    def __init__(self, flagQueueName: str = '', **kwargs):
        self.flagQueueName = flagQueueName

        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class CaptureFramesArgs:

    def __init__(self, height: int = 1920, width: int = 1080, fps: float = 30, rotationDegrees: int = 0, **kwargs):
        self.height = height
        self.width = width
        self.fps = fps
        self.rotationDegrees = rotationDegrees

        # Store or ignore unknown fields
        self.extra_fields = kwargs  # Optionally, store unknown fields for debugging or logging

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")

    def to_dict(self):
        """Return a dictionary representation excluding extra_fields."""
        filtered_parameters = {}

        for attribute_name, attribute_value in self.__dict__.items():
            if attribute_name != "extra_fields":
                filtered_parameters[attribute_name] = attribute_value

        return filtered_parameters

    def to_json(self):
        """Return a JSON string representation excluding extra_fields."""
        return json.dumps(self.to_dict())


class Package:

    def __init__(self, key: int = 0, packageTypeID: int = 0, fileID: int = 0, uRL: str = '', encrypted: int = 0, packageName: str = '', description: str = '', version: str = '', packageDate: datetime = None, creationDate: str = '', createdBy: int = 0, lastModifiedDate: int = '', lastModifiedBy: int = 0, **kwargs):
        self.packageID = key
        self.packageTypeID = packageTypeID
        self.fileID = fileID
        self.uRL = uRL
        self.encrypted = encrypted
        self.packageName = packageName
        self.description = description
        self.version = version
        self.packageDate = packageDate
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")


class Notification:

    def __init__(self, key: int = 0, notificationStatusID: int = 0, userID: int = 0, message: str = '', seenInApp: bool = False, seenDate: Optional[datetime] = None, sentAsEmail: bool = False, sentAsEmailDate: Optional[datetime] = None, guid: str = '', isArchived: bool = False, creationDate: Optional[datetime] = None, createdBy: int = 0, lastModifiedDate: Optional[datetime] = None, lastModifiedBy: int = 0, **kwargs):
        self.notificationID = key
        self.notificationStatusID = notificationStatusID
        self.userID = userID
        self.message = message
        self.seenInApp = seenInApp
        self.seenDate = seenDate
        self.sentAsEmail = sentAsEmail
        self.sentAsEmailDate = sentAsEmailDate
        self.guid = guid
        self.isArchived = isArchived
        self.creationDate = creationDate
        self.createdBy = createdBy
        self.lastModifiedDate = lastModifiedDate
        self.lastModifiedBy = lastModifiedBy
        # Optionally store any extra fields
        self.extra_fields = kwargs

        # Warn or log if there are unexpected keyword arguments
        if kwargs:
            print(f"Warning: Ignoring unexpected arguments: {kwargs}")
