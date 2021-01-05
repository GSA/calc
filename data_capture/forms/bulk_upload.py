from django import forms

from frontend.upload import UploadWidget
from ..r10_spreadsheet_converter import Region10SpreadsheetConverter


class Region10BulkUploadForm(forms.Form):
    '''
    Form for bulk upload of Region 10 data export
    '''
    file = forms.FileField(widget=UploadWidget(
        accept=('.xls', '.xlsx',),
        extra_instructions="Region 10 export file (XLS or XLSX), please."
    ))

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get('file')

        if file and not Region10SpreadsheetConverter(file).is_valid_file():
            raise forms.ValidationError("That file does not appear to be a "
                                        "valid Region 10 export. Try another?")

        return cleaned_data
