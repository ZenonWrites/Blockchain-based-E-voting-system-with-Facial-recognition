import os
import pytesseract
from PIL import Image
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import VerificationRequest
from .serializers import VerificationRequestSerializer
from django.conf import settings
from deepface import DeepFace  # Import DeepFace for face verification

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class UploadIDDocumentView(views.APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, format=None):
        # Create a new verification request or use the one from session
        verification_id = request.session.get('verification_id')
        
        if verification_id:
            try:
                verification = VerificationRequest.objects.get(id=verification_id)
            except VerificationRequest.DoesNotExist:
                verification = VerificationRequest.objects.create()
                request.session['verification_id'] = str(verification.id)
        else:
            verification = VerificationRequest.objects.create()
            request.session['verification_id'] = str(verification.id)
            
        # Save the ID document
        if 'id_document' in request.FILES:
            verification.id_document = request.FILES['id_document']
            verification.status = 'processing'
            verification.save()
            
            # Process the document using OCR
            try:
                extracted_data = self.extract_text_from_id(verification.id_document.path)
                
                # Update verification with extracted data
                verification.document_type = extracted_data.get('document_type', '')
                verification.document_number = extracted_data.get('document_number', '')
                verification.full_name = extracted_data.get('full_name', '')
                verification.date_of_birth = extracted_data.get('date_of_birth', '')
                verification.save()
                
                return Response({
                    'status': 'success',
                    'message': 'ID document uploaded and processed successfully',
                    'verification_id': verification.id,
                    'extracted_data': extracted_data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                verification.status = 'failed'
                verification.save()
                return Response({
                    'status': 'error',
                    'message': f'Error processing ID document: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'status': 'error',
                'message': 'No ID document provided'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def extract_text_from_id(self, image_path):
        """Extract text from ID document using Tesseract OCR."""
        img = Image.open(image_path)
        # Use Tesseract to extract raw text
        text = pytesseract.image_to_string(img)
        
        # Simple parsing logic for demonstration
        # In a real application, you would need more sophisticated parsing based on document type
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Basic extraction logic (this will need to be customized based on the ID format)
        document_type = 'Unknown'
        document_number = ''
        full_name = ''
        date_of_birth = ''
        
        # Very simple detection of document type
        if 'AADHAAR' in text or 'आधार' in text:
            document_type = 'Aadhaar'
        elif 'VOTER' in text or 'ELECTION' in text:
            document_type = 'Voter ID'
        elif 'DRIVING' in text or 'LICENCE' in text:
            document_type = 'Driver License'
        elif 'PASSPORT' in text:
            document_type = 'Passport'
            
        # Very basic extraction logic - would need to be much more sophisticated in reality
        for line in lines:
            if 'DOB' in line or 'Date of Birth' in line:
                date_of_birth = line
            # This is a very naive approach and would need to be improved for a real system
            if len(line) > 5 and len(line) < 50 and not document_number:
                # Assume a name or ID number
                if any(c.isdigit() for c in line) and len(line) < 20:
                    document_number = line
                elif all(c.isalpha() or c.isspace() for c in line):
                    full_name = line
        
        return {
            'document_type': document_type,
            'document_number': document_number,
            'full_name': full_name,
            'date_of_birth': date_of_birth,
            'raw_text': text
        }



class UploadSelfieView(views.APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, format=None):
        verification_id = request.session.get('verification_id')
        
        if not verification_id:
            return Response({
                'status': 'error',
                'message': 'No verification session found. Please upload an ID document first.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            verification = VerificationRequest.objects.get(id=verification_id)
        except VerificationRequest.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Verification request not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        if 'selfie' in request.FILES:
            verification.selfie_image = request.FILES['selfie']
            verification.save()
            
            # Only proceed if we have both images
            if verification.id_document and verification.selfie_image:
                try:
                    # Perform face matching using DeepFace
                    face_match_result = self.compare_faces(
                        verification.id_document.path, 
                        verification.selfie_image.path
                    )
                    
                    verification.face_match = face_match_result
                    verification.status = 'verified' if face_match_result else 'failed'
                    verification.save()
                    
                    return Response({
                        'status': 'success',
                        'message': 'Selfie uploaded and processed successfully',
                        'verification_id': verification.id,
                        'face_match': face_match_result,
                        'verification_status': verification.status
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    verification.status = 'failed'
                    verification.save()
                    return Response({
                        'status': 'error',
                        'message': f'Error processing selfie: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'status': 'success',
                    'message': 'Selfie uploaded. Please upload an ID document to complete verification.'
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'No selfie provided'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def compare_faces(self, id_image_path, selfie_image_path):
        """Compare faces between ID document and selfie using DeepFace."""
        try:
            # Use DeepFace to verify the two images
            result = DeepFace.verify(
                img1_path=id_image_path, 
                img2_path=selfie_image_path, 
                model_name='VGG-Face',  # You can choose other models like 'Facenet', 'OpenFace', etc.
                enforce_detection=False  # Set to False to avoid errors if no face is detected
            )
            return result['verified']  # Return True if faces match, otherwise False
        except Exception as e:
            # Log or handle exceptions if DeepFace fails
            print(f"DeepFace error: {e}")
            return False

class VerificationStatusView(views.APIView):
    def get(self, request, format=None):
        verification_id = request.session.get('verification_id')
        
        if not verification_id:
            return Response({
                'status': 'error',
                'message': 'No verification session found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        try:
            verification = VerificationRequest.objects.get(id=verification_id)
            serializer = VerificationRequestSerializer(verification)
            return Response({
                'status': 'success',
                'verification': serializer.data
            }, status=status.HTTP_200_OK)
        except VerificationRequest.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Verification request not found'
            }, status=status.HTTP_404_NOT_FOUND)