from django import forms
from .models import Review # Import your Review model

class ReviewForm(forms.ModelForm):
    # Explicitly define the image field as not required
    image = forms.ImageField(required=False, 
        widget=forms.FileInput(attrs={
            'class': 'mt-2 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-yellow-50 file:text-yellow-700 hover:file:bg-yellow-100'
        })
    )

    class Meta:
        model = Review
        fields = ['body', 'image'] # List the fields from your Review model that this form should handle
        widgets = {
            'body': forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-yellow-400 focus:outline-none resize-y",
                    "placeholder": "Write your review here...",
                    "rows": "4", # Retained 4 rows for better usability
                }
            ),
            # The 'image' field's widget is now defined above, so no need to repeat it here.
            # If you were to define it here, it would override the one above.
        }
