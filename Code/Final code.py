
import cv2
import face_recognition
import datetime
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from ibmcloudant.cloudant_v1 import CloudantV1
from ibmcloudant import CouchDbSessionAuthenticator
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator
import wiotp.sdk.device
import time
import random
myConfig = { 
    "identity": {
        "orgId": "aannkh",
        "typeId": "VITharish",
        "deviceId":"12345"
    },
    "auth": {
        "token": "9381628451"
    }
}

client = wiotp.sdk.device.DeviceClient(config=myConfig, logHandlers=None)
client.connect()

# Constants for IBM COS values
COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "XIzdVg_jB4YRIuitd-fz1LkP2OTbnFHpqE2v4NrBVg-F" # eg "W00YixxxxxxxxxxMB-odB-2ySfTrFBIQQWanc--P3byk"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/27c2eb7ce3824e58b9022d8e4ac34792:e0afac5f-48ad-492d-9f2e-4dd702111eaa::" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003xxxxxxxxxx1c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"

# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

authenticator = BasicAuthenticator('apikey-v2-h0ooew2msl6r4mla6of1nk1m75bz8cs16pbx4fch7dw', '0d52d202827e65107632ba94b4c7adc4')

service = CloudantV1(authenticator=authenticator)

service.set_service_url('https://apikey-v2-h0ooew2msl6r4mla6of1nk1m75bz8cs16pbx4fch7dw:0d52d202827e65107632ba94b4c7adc4@7f536afa-8bcf-495e-a4c8-1cf0e15dfdfe-bluemix.cloudantnosqldb.appdomain.cloud')
bucket = "harishdata"
def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))




mydoor = {'Door':'Hello Guest Please Place your Face infront of cam'}
client.publishEvent(eventId="status", msgFormat="json", data=mydoor, qos=0, onPublish=None)

video_capture = cv2.VideoCapture(0)

hari_image = face_recognition.load_image_file(r"photo.jpg")
hari_face_encoding = face_recognition.face_encodings(hari_image)[0]


harshith_image1 = face_recognition.load_image_file("harshith.jpeg")
harshith_face_encoding = face_recognition.face_encodings(harshith_image1)[0]

sreech_image = face_recognition.load_image_file(r"sreech.jpg")
sreech_face_encoding = face_recognition.face_encodings(sreech_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [hari_face_encoding,harshith_face_encoding,sreech_face_encoding]

known_face_names = [
    "Harish",
    "Harshith",
    "charan",
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        #mydoor = {'Door':'Hello Guest Please Place your Face infront of cam'}
        cv2.imshow('Video', frame)
        picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
        cv2.imwrite(picname+".jpg",frame)
        '''multi_part_upload(bucket, picname+'.jpg', picname+'.jpg')
        json_document={"link":COS_ENDPOINT+'/'+bucket+'/'+picname+'.jpg'}
        response = service.post_document(db='sample1', document=json_document).get_result()'''
        def myCommandCallback(cmd):
            print("Message received from IBM IoT Platform: %s" % cmd.data['command'])
            m=cmd.data['command']
            if (m =="true"):
                if name in known_face_names:
                    mydata = {'Guest':True}
                    mydoor = {'Door':[name,'Guest is recognised door is opening.....']}
                else:
                    mydata = {'Guest':False}
                    mydoor = {'Door':'Guest is not recognised if you want to open please press open button to open door'}
        #client.publishEvent(eventId="status", msgFormat="json", data=mydoor1, qos=0, onPublish=None)
                client.publishEvent(eventId="status", msgFormat="json", data=mydata, qos=0, onPublish=None)
                client.publishEvent(eventId="status", msgFormat="json", data=mydoor, qos=0, onPublish=None)
                print("Published data Successfully: %s", mydata)
                time.sleep(2)
            else:
                mydoor = {'Door':'Hello Guest Please Place your Face infront of camera'}
                client.publishEvent(eventId="status", msgFormat="json", data=mydoor, qos=0, onPublish=None)
        client.commandCallback = myCommandCallback
        multi_part_upload(bucket, picname+'.jpg', picname+'.jpg')
        json_document={"link":COS_ENDPOINT+'/'+bucket+'/'+picname+'.jpg'}
        response = service.post_document(db='sample1', document=json_document).get_result()


    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
mydoor = {'Door':'Hello Guest Please Place your Face infront of camera and press get image'}
client.publishEvent(eventId="status", msgFormat="json", data=mydoor, qos=0, onPublish=None)
video_capture.release()
cv2.destroyAllWindows()
client.disconnect()


# In[ ]:





# In[ ]:




