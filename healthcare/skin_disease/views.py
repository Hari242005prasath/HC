from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai  # Correct import

# Configure Google API Key
GOOGLE_API_KEY = "AIzaSyCdiv3JmZsAtBtzzetw3Zre8hz635PqS50"
genai.configure(api_key=GOOGLE_API_KEY)

@csrf_exempt
def generate_skin_report(request):
    if request.method == "POST":
        disease_name = request.POST.get("disease_name", "").strip()
        age = request.POST.get("age", "").strip()
        skin_type = request.POST.get("skin_type", "").strip()
        severity = request.POST.get("severity", "").strip()

        # Validate inputs
        if not disease_name:
            return JsonResponse({"error": "Please provide a disease name."}, status=400)
        if not age.isdigit():
            return JsonResponse({"error": "Please provide a valid age."}, status=400)

        # Create prompt
        prompt = (
            f"Provide a detailed treatment plan for {disease_name}. "
            f"The patient is {age} years old, has {skin_type} skin, and the disease severity is {severity}. "
            f"Suggest medical treatments, home remedies, and precautions."
        )

        try:
            # Load Gemini model
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Generate content correctly
            response = model.generate_content(prompt)

            # Extract text properly
            generated_text = response.text if hasattr(response, "text") else "No response generated."

            return JsonResponse({"plan": generated_text.replace("*", "").strip()})

        except genai.types.GenerativeAIError as api_error:
            print("Google API Error:", str(api_error))
            return JsonResponse({"error": f"Google API Error: {str(api_error)}"}, status=500)

        except Exception as e:
            print("Unexpected Error:", str(e))
            return JsonResponse({"error": f"Error generating treatment plan: {str(e)}"}, status=500)

    return render(request, "generate_report.html")
