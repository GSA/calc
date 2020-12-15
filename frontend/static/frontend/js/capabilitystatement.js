/* eslint-disable */
function radioButtonChanged(selectedValue) {
  const fileUpload = document.getElementById("fileUpload");
  const urlUpload = document.getElementById("urlUpload");
  if (selectedValue === "url") {
    fileUpload.style.display = "none";
    urlUpload.style.display = "block";
    document.getElementById('id_file').required = false;
    document.getElementById('id_url').required = true;
  }
  if (selectedValue === "file") {
    urlUpload.style.display = "none";
    fileUpload.style.display = "block";
    document.getElementById('id_url').required = false;
    document.getElementById('id_file').required = true;
  }
}

function formHTTPValidaion() {
  radio = $('input[name = "file_upload_option"]:checked').val();
  if (radio === "file") {
    return true;
  } else {
    url = $('#id_url').val();
    if (url.indexOf('http') !== -1) {
      return true;
    } else {
      urlHttp = "http://"+url;
      $('#id_url').val(urlHttp);
      return true;
    }    
  }
}

function filechanged(el) {   
  const filename = el.files[0].name;
  if (filename !== "") {
    $('.file_name_holder').text(filename);
    $('.upload-chooser').removeClass('inactive').addClass('active');
    $('.upload-chooser label').text('choose a different file');
  } else {
    $('.file_name_holder').text("");
    $('.upload-chooser').removeClass('active').addClass('inactive');
    $('.upload-chooser label').text('choose file');
  }    
}

function dragOverHandler(ev) {
  ev.preventDefault();
  ev.stopPropagation();
}

function addFiles(ev) {
  ev.preventDefault();
  ev.stopPropagation();
  fileInput = document.getElementById('id_file');
  draggedFilename = ev.dataTransfer.files[0].name.split('.');
  extension = draggedFilename[1];
  if (extension.toLowerCase() !== "pdf" && extension.toLowerCase() !== "docx") {
    alert("Please Select PDF or DOCX file type");
    ev.preventDefault();
    ev.stopPropagation();
  } else {
    fileInput.files = ev.dataTransfer.files;
    filechanged(fileInput);
  } 
}
