/* eslint-disable */
$(document).ready(() => {
  const currentPage = window.location.href;
  let API_URL = "https://calc.gsa.gov"
  if(currentPage.indexOf('localhost') != -1){
    API_URL = "http://localhost:8000"
  }
  else if(currentPage.indexOf('calc-dev') != -1){
    API_URL = "https://calc-dev.app.cloud.gov"
  }
  else if(currentPage.indexOf('calc.gsa') != -1){
    API_URL = "https://calc.gsa.gov"
  }
  

  showWarningBanner = () => {
    deactivateLoader();
    $('.primary_form').hide();
    $('.warnningbanner').show();
  }
  // $(function() { 
  //   var timeOutObj;
  //   var xhr = $.get({
  //     //beforeSend: activateLoader(),
  //     url:'https://oasispet.gsa.gov/cpet/view/105495',
  //     success:() => {
  //       deactivateLoader();
  //       clearTimeout(timeOutObj); // API success so stoping the timer
  //       return;
  //     }
  //   });
  //   timeOutObj = setTimeout(()=>{
  //     xhr.abort();
  //     showWarningBanner() //showing warning banner if API take more than 5 sec time
  //   },50000)
  // });

  setWageOption = (res) => {
    res.data.map(d => {
        $('#radioWageScaleOption1_junior').text('').text('$' + d.h_pct10);
        $('#radioWageScaleOption1_journey').text('').text('$' + d.h_pct25);
        $('#radioWageScaleOption1_senior').text('').text('$' + d.h_pct50);
        $('#radioWageScaleOption1_expert').text('').text('$' + d.h_pct75);

        $('#radioWageScaleOption2_junior').text('').text('$' + d.h_pct25);
        $('#radioWageScaleOption2_journey').text('').text('$' + d.h_pct50);
        $('#radioWageScaleOption2_senior').text('').text('$' + d.h_pct75);
        $('#radioWageScaleOption2_expert').text('').text('$' + d.h_pct90);

        $('#radioWageScaleOption3_junior').text('').text('$' + d.h_pct50);
        $('#radioWageScaleOption3_journey').text('').text('$' + d.h_pct75);
        $('#radioWageScaleOption3_senior').text('').text('$' + d.h_pct90);
        $('#radioWageScaleOption3_expert').text('').text('$' + d.h_pct90);
    });
  };

  activateLoader = (elmt) => {
    $('.valueList').find('.loader_item').remove()//<div class="loader_item"></div>
    $(elmt).parent().append('<div class="loader_item"></div>');
  };

  deactivateLoader = () => {
    $('.valueList').find('.loader_item').remove();
  };

  getWageScaleOptions = (val,el) => {
    const occupation = $('#selectOccupation').val();
    const area = $('#selectMsa').val();
    if (occupation !== "" && area != "") {
      $.post({
        beforeSend: activateLoader(el),
        url: API_URL+"/api/bls_pet/getprice",
        data: {
          "occupation_code": occupation,
          "area":area
        },
        success: (res) => {
          deactivateLoader();
          setWageOption(res);
        }
      });
    }
  };

  createMSA = (el) => {
    const statecode = $(el).val();
    if (statecode !== "") {
      $.post({
        beforeSend: activateLoader(el),
        url: API_URL+"/api/bls_pet/autocomplete/area/",
        data: {
          "statecode": statecode,
          "occupation":$('#selectOccupation').val()
        },
        success: (res) => {
          deactivateLoader();
          optionData = `<option value=''>Select One Area</option>`;
          res.data.map(d => {
            optionData += `<option value='${d.city}'>${d.city}</option>`;
          });
          $('#selectMsa').removeAttr('disabled').empty().append(optionData);               
        }
      });
    }
  }

  createIndirectRateLevel = (el) => {
    activateLoader(el);
    const indirectData = ['Low', 'Average', 'High'];
    optionData = "<option value=''>Choose one...</option>";
    for (i = 0; i < indirectData.length; i ++) {
      optionData += "<option value=" + indirectData[i] + ">" + indirectData[i] + "</option>";
    }
    $('#selectIndirectRateLevel').removeAttr('disabled').empty().append(optionData);
    deactivateLoader();
        
  };

  

  callForStateList = () => {
    const stateElement = $('#selectState');
    $.post({
      beforeSend: activateLoader(stateElement),
      data:{"occupation":$('#selectOccupation').val()},
      url: API_URL+"/api/bls_pet/autocomplete/state/",
      success: (res) => {
        deactivateLoader();
        optionData = `<option data-attr_dbid='' value=''>Choose one...</option>`;
        res.data.map(st => {
          optionData += `<option data-attr_dbid='${st.id}' value='${st.code}'>${st.state}</option>`;
        });
        $(stateElement).removeAttr('disabled').empty().append(optionData);     
      }
    });
  };

  getLACTTitle = (el) => {        
    const value_occupation = $(el).val();
    console.log(value_occupation);
    if (value_occupation != "") {
      $.post({
        beforeSend: activateLoader(el),
        url: API_URL+"/api/bls_pet/autocomplete/lcat/",
        data:{"occ_id":value_occupation},
        success: (res) => {
          $('#fldLcatTitle').val(res.data.lcat_details[0].lcat_title);
          $('#fldLcatValue').val(res.data.lcat_details[0].lcat_id);
          $('#selectEnqLevel').empty().append(`<option value="">Choose one...</option>`);
          res.data.eandqlevels.map(data => {
            $('#selectEnqLevel').append(`<option value="${data.value}">${data.description}</option>`)
          });
          $('#selectEnqLevel').removeAttr('disabled');
          deactivateLoader();
          callForStateList();
        }
      });
    }
  };

  launchPriceIndex = () => {
    $('.primary_form').hide();
    $('.results').hide()
    $('.secondary_form').show();
  };

  objectifyForm = (formArray) => {
    var returnArray = {};
    for (var i = 0; i < formArray.length; i++){
      returnArray[formArray[i]['name']] = formArray[i]['value'];
    }
    return returnArray;
  };
  goback = () => {
    resetFinalResetSet();
    $('.results').hide();
    $('.secondary_form').hide();  
    $('.primary_form').show();      
  };


  function resetFinalResetSet () {
    $('.primary_form').trigger('reset');
    $('.secondary_form').trigger('reset');
    $('.igce_summary').find('#occ').text('')
    $('.igce_summary').find('#eandq').text('')
    $('.igce_summary').find('#msa').text('')
    $('.igce_summary').find('#wagescale').text('')
    $('.igce_summary').find('#in_rate_level').text('')
    $('.igce_summary').find('#cmds').text('')


    resultsTableids = ['igce_details_1','igce_details_2','igce_details_3','igce_details_4','igce_details_5']
    
    $.each(resultsTableids,(index,element) => {
      
      tbodyEle = document.querySelector('.'+element)
      $(tbodyEle).find('.result_occupation').text('')
      $(tbodyEle).find('.result_eandq').text('')
      $(tbodyEle).find('.result_msa').text('')
      $(tbodyEle).find('.result_est_hour').text('')
      $(tbodyEle).find('.result_est_hour_rate').text('')
      $(tbodyEle).find('.result_total').text('');
    });
    $('.igce_summary').find('#lcat_est').text('');
  }


  filleIndirectRateDisplay = (el) => {
    $('#IndirectRateLevelDisplay').val($(el).find("option:selected").text());
  };

  function getFinalPricePerYear(hour,baseprice){
    const priceToBeAdded = additionalPrice[hour]
    return parseFloat(baseprice)+parseFloat(priceToBeAdded)
  }
  validateSecondary = (el) => {
    primary_form_data = objectifyForm($('.primary_form').serializeArray());
    secondary_form_data = objectifyForm($('.secondary_form').serializeArray());
    $.ajax({
      type:"POST",
      beforeSend: activateLoader(el),
      url: API_URL+"/api/bls_pet/getblswage",
      data: {
        "occ_id": secondary_form_data['socCode'],
        "area": secondary_form_data['msa']
      },
      success: (results) => {
        console.log(results);
        deactivateLoader();
        if(results['Error'] == 0){
          occupationSelected = $('#selectOccupation').find('option:selected').text()+'( '+secondary_form_data['socCode']+')'
     
          $('.igce_summary').find('#occ').text(occupationSelected)
          $('.igce_summary').find('#eandq').text(secondary_form_data['eqLevel'])
          $('.igce_summary').find('#msa').text(secondary_form_data['msa'])
          $('.igce_summary').find('#wagescale').text(secondary_form_data['radioWageScaleOption'])
          $('.igce_summary').find('#in_rate_level').text(secondary_form_data['markupPercent'])
          $('.igce_summary').find('#cmds').text(secondary_form_data['comments'])


          resultsTableids = ['igce_details_1','igce_details_2','igce_details_3','igce_details_4','igce_details_5']
          let totlaPrice = 0;
          $.each(resultsTableids,(index,element) => {
            const estId = 'fldEstimatedHours'+(index+1)
            estHour = document.getElementById(estId).value
            const orderYear = 'order_year_'+(index+1)
            if(index > 0){
              orderYearSpan = document.querySelector('.'+orderYear)
              orderYearSpan.innerHTML = estHour
            }
            const updatedprice = getFinalPricePerYear(estHour,results['data']['value'])
            const price = updatedprice*estHour
            totlaPrice = price+totlaPrice;
            tbodyEle = document.querySelector('.'+element)
            $(tbodyEle).find('.result_occupation').text(occupationSelected)
            $(tbodyEle).find('.result_eandq').text(secondary_form_data['eqLevel'])
            $(tbodyEle).find('.result_msa').text(secondary_form_data['msa'])
            $(tbodyEle).find('.result_est_hour').text(estHour)
            $(tbodyEle).find('.result_est_hour_rate').text(updatedprice.toFixed(2))
            $(tbodyEle).find('.result_total').text(price.toFixed(2))
          });
          $('.igce_summary').find('#lcat_est').text(totlaPrice.toFixed(2));
          $('.primary_form').hide();
          $('.secondary_form').hide();
          $('.results').show();
        }else{
          alert(results['Error_Message'])
        }
        
      }
    });
    return false;  
  };
  var primary_data;
  var secondary_data;
  validatePrimary = (form_el) => {
    primary_data = $(form_el).serializeArray();
    launchPriceIndex();
    return false;
  };

 var additionalPrice;
 function getAddtionalPriceList(){
  $.get({
    url: API_URL+"/api/bls_pet/autocomplete/additional_price/",
    success: (res) => {
      additionalPrice = res.data;
    }
  });
 } 
 function getAllOccupation(){
   const el = $('#selectOccupation');
   const el_err = $('#selectOccupation_error');
  $.get({
    beforeSend: activateLoader(el),
    url: "/api/bls_pet/autocomplete/occupation/",
    success: (res) => {
      if (res.Error != 0){
        $(el_err).text(res.ErrorMessage);return false;
      }
      const values = res.data;
      $(el).empty().append(`<option value="">Select One Occupation</option>`)
      values.map(eachVal => {
        $(el).append(`<option value="${eachVal.code}">${eachVal.occupation}</option>`);
      });
      $(el).removeAttr('disabled');
      deactivateLoader();
      
    }
  });
  }


  getAllOccupation();
  getAddtionalPriceList();
});
