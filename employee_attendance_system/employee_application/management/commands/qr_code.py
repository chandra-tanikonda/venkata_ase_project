import cv2
import openpyxl
import webbrowser
from django.core.management.base import BaseCommand

import cv2
import webbrowser
from django.utils import timezone
from employee_application.models import Employee, EmployeeAttendanceRecord

def open_web_browser_for_qr_code_scan():
    """
    Function to scan a QR code using the webcam.
    When a QR code is detected, it opens the URL encoded in it in a web browser,
    and updates or creates an attendance record for the associated employee.
    """
    # Initialize the QRCode detector
    qr_detector = cv2.QRCodeDetector()

    # Start capturing video from the webcam
    video_capture = cv2.VideoCapture(0)

    # Check if the webcam is successfully opened
    if not video_capture.isOpened():
        print("Error: Couldn't open the webcam.")
        return

    # Loop to continuously capture frames from the webcam
    while True:
        # Read a frame from the webcam
        video_capture_resp, video_frame = video_capture.read()

        # Check if the frame was successfully captured
        if not video_capture_resp:
            print("Error: Couldn't read the frame.")
            break

        # Display the captured frame in a window named 'frame'
        cv2.imshow("frame", video_frame)

        # Attempt to detect and decode a QR code in the frame
        qr_value, bbox, _ = qr_detector.detectAndDecode(video_frame)

        # If a QR code is detected and decoded
        if qr_value:
            print("QR Code Value:", qr_value)

            # Open the decoded URL in a web browser
            webbrowser.open(qr_value)

            # Attempt to find an employee with the matching unique QR code
            employee = Employee.objects.filter(employee_identifier=qr_value).first()
            if not employee:
                print(f"No employee associated with QR code: {qr_value}")
                continue  # Skip to the next QR code if no employee is found

            # Get today's date
            today = timezone.now().date()
            # Check if an attendance record already exists for today
            attendance_record, created = EmployeeAttendanceRecord.objects.get_or_create(
                employee=employee,
                attendance_date=today,
            )

            # Provide feedback based on whether the record was created or already existed
            if created:
                print(f"Attendance recorded for: {employee.username}")
            else:
                print(f"Today's attendance already recorded for: {employee.username}")

            # Release the webcam and close the display window
            video_capture.release()
            cv2.destroyAllWindows()
            return  # Exit the function after handling one QR code

        # Wait for 1 ms and check if the ESC key is pressed to exit
        if cv2.waitKey(1) == 27:  # ESC key
            break

    # Release the webcam and close all OpenCV windows
    video_capture.release()
    cv2.destroyAllWindows()

class Command(BaseCommand):
    help = 'Generate the QR code and scan the QR code value.'

    def handle(self, *args, **kwargs):
        open_web_browser_for_qr_code_scan()
