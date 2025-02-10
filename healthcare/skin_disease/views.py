from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

# Configure Google API Key
genai.configure(api_key="AIzaSyCdiv3JmZsAtBtzzetw3Zre8hz635PqS50")

@csrf_exempt
def generate_skin_report(request):
    if request.method == "POST":
        disease_name = request.POST.get("disease_name", "").strip()
        age = request.POST.get("age", "").strip()
        skin_type = request.POST.get("skin_type", "").strip()
        severity = request.POST.get("severity", "").strip()

        if not disease_name:
            return JsonResponse({"error": "Please provide a disease name."}, status=400)
        if not age.isdigit():
            return JsonResponse({"error": "Please provide a valid age."}, status=400)

        # Create AI prompt
        prompt = (
            f"Provide a detailed treatment plan for {disease_name}. "
            f"The patient is {age} years old, has {skin_type} skin, and the disease severity is {severity}. "
            f"Suggest medical treatments, home remedies, and precautions."
        )

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            generated_text = response.text if hasattr(response, "text") else "No response generated."

            # Generate PDF
            pdf_buffer = BytesIO()
            pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

            # Set margins (5 cm ≈ 142 points)
            margin = 142
            width, height = letter
            max_width = width - (2 * margin)  # Maximum text width
            y_position = height - margin

            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawCentredString(width / 2, y_position, "Skin Disease Report")
            y_position -= 30

            pdf.setFont("Helvetica", 12)
            pdf.drawString(margin, y_position, f"Disease: {disease_name}")
            y_position -= 20
            pdf.drawString(margin, y_position, f"Age: {age}")
            y_position -= 20
            pdf.drawString(margin, y_position, f"Skin Type: {skin_type}")
            y_position -= 20
            pdf.drawString(margin, y_position, f"Severity: {severity}")
            y_position -= 40  # Space before content

            # Formatting AI Response
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(margin, y_position, "Treatment Plan:")
            y_position -= 25

            pdf.setFont("Helvetica", 11)
            for line in generated_text.split("\n"):
                wrapped_lines = simpleSplit(line, "Helvetica", 11, max_width)
                for wrapped_line in wrapped_lines:
                    if y_position <= margin:
                        pdf.showPage()
                        pdf.setFont("Helvetica", 11)
                        y_position = height - margin
                    pdf.drawString(margin, y_position, wrapped_line)
                    y_position -= 18  # Line spacing

            pdf.save()
            pdf_buffer.seek(0)

            response = HttpResponse(pdf_buffer, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="skin_disease_report.pdf"'
            return response

        except genai.types.GenerativeAIError as api_error:
            return JsonResponse({"error": f"Google API Error: {str(api_error)}"}, status=500)

        except Exception as e:
            return JsonResponse({"error": f"Error generating report: {str(e)}"}, status=500)

    return render(request, "generate_report.html")

def myself(request):
    return render(request,'index.html')

import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

API_KEY = "AIzaSyBEjuyLDRRxkYef3KzBkbDO_xzEpDJMlTs"  # Replace with a secure API key
genai.configure(api_key=API_KEY)

# Store chat history in session
@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            # Retrieve previous chat history from session
            chat_history = request.session.get("chat_history", [])

            # Gemini Prompt to ensure remedies or clarifications
            prompt = (
                f"Previous Chat:\n{chat_history}\n\n"
                f"User: {user_message}\n"
                "Respond concisely in 10 words or fewer. "
                "Do not ask questions. Only provide direct and meaningful answers."
            )




            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            response_text = response.text.strip()

            # Update chat history
            chat_history.append({"user": user_message, "bot": response_text})
            request.session["chat_history"] = chat_history

            return JsonResponse({"response": response_text, "chat_history": chat_history})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request"}, status=400)
