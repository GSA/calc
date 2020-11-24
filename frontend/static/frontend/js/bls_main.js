/* eslint-disable */
$(document).ready(() => {
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
    const lcat_id = $('#fldLcatValue').val();
    const area_id = $('#selectMsa').val();
    if (occupation !== "" && area_id != "" && lcat_id!= "") {
      $.post({
        beforeSend: activateLoader(el),
        url: "http://localhost:8000/api/bls_pet/getprice",
        data: {
          "lcat_id": lcat_id,
          "occupation_code": occupation,
          "area_id":area_id
        },
        success: (res) => {
          deactivateLoader();
          setWageOption(res);
        }
      });
    }
  };

  createMSA = (el) => {
    const state_value = $(el).val();
    if (state_value !== "") {
      $.post({
        beforeSend: activateLoader(el),
        url: "http://localhost:8000/api/bls_pet/autocomplete/area/",
        data: {
          "state_code": state_value,
        },
        success: (res) => {
          deactivateLoader();
          optionData = '';
          res.data.map(d => {
            optionData += `<option value='${d.id}'>${d.city}</option>`;
          });
          $('#selectMsa').removeAttr('disabled').empty().append(optionData);
          // if (res.data.length > 0) {
          //   getWageScaleOptions(res[0]['sMsa'],$('#selectMsa'));
          // }                   
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
    $.get({
      beforeSend: activateLoader(stateElement),
      url: "http://localhost:8000/api/bls_pet/autocomplete/state/",
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
        url: "http://localhost:8000/api/bls_pet/autocomplete/lcat/",
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
    $('.bls_result_tbody').empty();
    $('.bls_result').hide();
    $('.primary_form').hide();
    $('.secondary_form').show();        
  };
  filleIndirectRateDisplay = (el) => {
    $('#IndirectRateLevelDisplay').val($(el).find("option:selected").text());
  };
  launchResult = (el) => {
    $('.primary_form').hide();
    $('.secondary_form').hide();
    primary_form_data = objectifyForm($('.primary_form').serializeArray());
    secondary_form_data = objectifyForm($('.secondary_form').serializeArray());
    console.log(primary_form_data);
    console.log(secondary_form_data);
    // $.get({
    //   beforeSend: activateLoader(el),
    //   url: "https://oasispet.gsa.gov/cpet/cpetPricingTool/generateMsaWages",
    //   data: {
    //     "cpetId": primary_form_data['cpetId'],
    //     "sEQLevel": secondary_form_data['eqLevel'],
    //     "sMsa": secondary_form_data['msa'],
    //     "sSocCode": secondary_form_data['socCode'],
    //     "sWageScale": secondary_form_data['radioWageScaleOption'],
    //     "sMarkupPercent": secondary_form_data['markupPercent'],
    //     "IndirectRateLevelDisplay": secondary_form_data['IndirectRateLevelDisplay'],
    //     "sEstimateHours1": secondary_form_data['estimatedHours1'],
    //     "sEstimateHours2": secondary_form_data['estimatedHours2'],
    //     "sEstimateHours3": secondary_form_data['estimatedHours3'],
    //     "sEstimateHours4": secondary_form_data['estimatedHours4'],
    //     "sEstimateHours5": secondary_form_data['estimatedHours5'],
    //   },
    //   success: (res) => {
    //     console.log(res);
    //     deactivateLoader();
    //     trdata = "<tr>";
    //     trdata += "<td>" + res.titleSoc + "</td>";
    //     trdata += "<td>" + res.eqLcatTile + "</td>";
    //     trdata += "<td>" + res.stateMsa + "</td>";
    //     trdata += "<td>" + res.hoursEstimate + "</td>";
    //     trdata += "<td>$" + res.estHourlyRate + "</td>";
    //     trdata += "<td>$" + res.totalEstAmount + "</td>";
    //     trdata += "<tr>";
    //     $('.bls_result_tbody').empty().append(trdata)
    //     $('.bls_result').show();
    //   }
    // });
    return false;  
  };
  var primary_data;
  var secondary_data;
  validatePrimary = (form_el) => {
    primary_data = $(form_el).serializeArray();
    launchPriceIndex();
    return false;
  };
  validateSecondary = (form_el) => {
    secondary_data = $(form_el).serializeArray();
    launchResult($('.get_result_btn'));
    return false;
  };


 function getAllOccupation(){
   const el = $('#selectOccupation');
   const el_err = $('#selectOccupation_error');
  $.get({
    beforeSend: activateLoader(el),
    url: "http://localhost:8000/api/bls_pet/autocomplete/occupation/",
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


  getAllOccupation()
});
