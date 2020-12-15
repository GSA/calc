import os
import boto3
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

from data_capture.models import capability_statement as CapSta
from ..management.commands.initgroups import ANALYZE_PRICES_PERMISSION
from django.conf import settings
from django.core.files.storage import FileSystemStorage
# from data_capture.models import capability_statement as conSta


@login_required
@permission_required(ANALYZE_PRICES_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
def add_capability_statment(request):
    form_submitted = 0
    if request.method == 'POST':
        print(request.POST['file_upload_option'])
        if request.POST['file_upload_option'] == "url":
            giveUrl = request.POST['capability_url']
            givenContractNumber = request.POST['contract_number']

            # checking the given contract number already there
            capabilityStatementInstance = CapSta.objects.filter(contract_number=str
                                                                (givenContractNumber))
            if capabilityStatementInstance:  # if exists,updating the old one
                capabilityStatementInstance = capabilityStatementInstance[0]
                capabilityStatementInstance.url = str(giveUrl)
                capabilityStatementInstance.save()
                uploaded_file_status = "Given URL updated successfully"
            else:  # if not exists,creating one
                capabilityStatementInstance = CapSta(
                    contract_number=str(givenContractNumber),
                    url=str(giveUrl)
                )
                capabilityStatementInstance.save()
                uploaded_file_status = "Given URL added successfully"
            form_submitted = 1
            return render(request, '../../data_explorer/templates/step_cap.html', {
                'uploaded_file_status': uploaded_file_status,
                'form_submitted': form_submitted
            })
        elif request.POST['file_upload_option'] == "file":
            myfile = request.FILES['capability_file']
            fs = FileSystemStorage()
            # checking the given contract number already there in Database
            capabilityStatementInstance = CapSta.objects.filter(contract_number=str
                                                                (request.POST['contract_number']))
            if capabilityStatementInstance:  # if exists,deleting from database
                capabilityStatementInstance.delete()
            # deleting if the contract number alreay there
            allow_extensions = ['.pdf', '.docx', '.doc']
            for ext in allow_extensions:
                if os.path.exists(os.getcwd() + "/calc/capability_statement_files/" +
                                  str(request.POST['contract_number']) + ext):
                    os.remove(os.getcwd() + "/calc/capability_statement_files/" +
                              str(request.POST['contract_number']) + ext)

            filename_arry = myfile.name.split('.')
            file_extension = filename_arry[-1]

            fs.save(os.getcwd() + "/calc/capability_statement_files/" +
                    str(request.POST['contract_number'] + "." + file_extension), myfile)
            try:
                local_directory = os.getcwd() + "/calc/capability_statement_files/"
                AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
                AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
                AWS_REGION = settings.AWS_REGION
                AWS_BUCKET = settings.AWS_STORAGE_BUCKET_NAME

                file_to_upload = str(request.POST['contract_number'] + "." + file_extension)
                local_path = os.path.join(local_directory, file_to_upload)
                key = file_to_upload
                s3_client = boto3.client('s3', AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                s3_client.upload_file(local_path, AWS_BUCKET, key, ExtraArgs={
                                      'ContentType': 'application/' + file_extension,
                                      'ACL': 'public-read'})
                uploaded_file_status = "File Uploaded Successfully"
                form_submitted = 1

            except Exception:
                uploaded_file_status = "Error While File Uploading"
                form_submitted = 2

            # removing file from folder once the file uploaded
            for ext in allow_extensions:
                if os.path.exists(os.getcwd() + "/calc/capability_statement_files/" +
                                  str(request.POST['contract_number']) + ext):
                    os.remove(os.getcwd() + "/calc/capability_statement_files/" +
                              str(request.POST['contract_number']) + ext)
            return render(request, '../../data_explorer/templates/step_cap.html', {
                'uploaded_file_status': uploaded_file_status,
                'form_submitted': form_submitted
            })
        else:
            return render(request, '../../data_explorer/templates/step_cap.html', {
                'uploaded_file_url': "Error While File Uploading",
                'form_submitted': form_submitted
            })

    return render(request, '../../data_explorer/templates/step_cap.html', {
        'uploaded_file_url': "Error While File Uploading",
        'form_submitted': form_submitted})
