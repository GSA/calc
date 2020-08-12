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

  setWageOption = (data) => {      
    data = [
      { 
        " level": "Lowest Scale", " EQ1": "29.88", " EQ2": "31.19", " EQ3": "33.34", " EQ4": "35.49" 
      },
      { 
        " level": "Medium Scale", " EQ1": "31.19", " EQ2": "33.34", " EQ3": "35.49", " EQ4": "50.02" 
      },
      { 
        " level": "Highest Scale", " EQ1": "33.34", " EQ2": "35.49", " EQ3": "50.02", " EQ4": "58.04" 
      }];

    data.map(d => {
      if (d.level === "Lowest Scale") {
        $('#radioWageScaleOption1_junior').text('').text('$' + d.EQ1);
        $('#radioWageScaleOption1_journey').text('').text('$' + d.EQ2);
        $('#radioWageScaleOption1_senior').text('').text('$' + d.EQ3);
        $('#radioWageScaleOption1_expert').text('').text('$' + d.EQ4);
      } else if (d.level === "Medium Scale") {
        $('#radioWageScaleOption2_junior').text('').text('$' + d.EQ1);
        $('#radioWageScaleOption2_journey').text('').text('$' + d.EQ2);
        $('#radioWageScaleOption2_senior').text('').text('$' + d.EQ3);
        $('#radioWageScaleOption2_expert').text('').text('$' + d.EQ4);
      } else if (d.level === "Highest Scale") {
        $('#radioWageScaleOption3_junior').text('').text('$' + d.EQ1);
        $('#radioWageScaleOption3_journey').text('').text('$' + d.EQ2);
        $('#radioWageScaleOption3_senior').text('').text('$' + d.EQ3);
        $('#radioWageScaleOption3_expert').text('').text('$' + d.EQ4);
      }
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
    const sMsa = val;
    const SocCode = $('#selectOccupation').val();
    if (sMsa !== "") {
      $.get({
        beforeSend: activateLoader(el),
        url: "https://oasispet.gsa.gov/cpet/cpetPricingTool/wageScaleOption",
        data: {
          "sMsa": sMsa,
          "sSocCode": SocCode
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
    const occupation = $('#selectOccupation').val();
    if (state_value !== "") {
      $.get({
        beforeSend: activateLoader(el),
        url: "https://oasispet.gsa.gov/cpet/cpetPricingTool/stateMSAList",
        data: {
          "sState": state_value,
          "sSocCode": occupation
        },
        success: (res) => {
          deactivateLoader();
          optionData = '';
          res.map(d => {
            optionData += "<option value='" + d.sMsa+"'>" + d.sMsa + "</option>";
          });
          $('#selectMsa').removeAttr('disabled').empty().append(optionData);
          if (res.length > 0) {
            getWageScaleOptions(res[0]['sMsa'],$('#selectMsa'));
          }                   
        }
      });
    }
  }

  createIndirectRateLevel = (el) => {
    const eandq_vallue = $(el).val();
    const lcat_value = $('#fldLcatValue').val();
    const cpetId = $('#cpetId').val();
    $.get({
      beforeSend: activateLoader(el),
      url: "https://oasispet.gsa.gov/cpet/cpetPricingTool/markupPercent",
      data: {
        "sEQLevel": eandq_vallue,
        "iLCatId": lcat_value,
        "cpetId": cpetId,
      },
        success: (res) => {
        deactivateLoader();
        const indirectData = ['Low', 'Average', 'High'];
        optionData = "<option value=''>Choose one...</option>";
        for (i = 0; i < res.length; i ++) {
          optionData += "<option value=" + res[i] + ">" + indirectData[i] + "</option>";
        }
        $('#selectIndirectRateLevel').removeAttr('disabled').empty().append(optionData);
      }
    });
  };
  createEANDQLevel = (lcatId) => {
    eandqData = [
      {
        "value": "JR", "description": "Junior"
      }, {
        "value": "JY", "description": "Journeyman"
      }, {
        "value": "SR", "description": "Senior"
      }, {
        "value": "XP", "description": "SME"
      },
    ]
    if (lcatId === 14 || lcatId === 1 || lcatId === 12 || lcatId === 5) {
      eandqData = [
        {
          "value": "JR", "description": "Junior"
        }, {
          "value": "JY", "description": "Journeyman"
        }, {
          "value": "SR", "description": "Senior"
        }, {
          "value": "XP", "description": "SME"
        },
      ]
    } else if (lcatId === 27) {
      eandqData = [
        {
          "value": "JR", "description": "WL1"
        }, {
          "value": "JY", "description": "WL2"
        }, {
          "value": "SR", "description": "WL3"
        }, {
          "value": "XP", "description": "WL4"
        },
      ]
    }
    optionData = "<option value=''>Choose one...</option>";
    eandqData.map(d => {
      optionData += "<option value='" + d.value + "'>" + d.description + "</option>";
    });
    $('#selectEnqLevel').removeAttr('disabled').empty().append(optionData);
  }

  createStateOptions = (el, data) => {
    optionData = "<option value=''>Choose one...</option>";
    data.map(d => {
      optionData += "<option value='" + d.state+"'>" + d.description + "</option>";
    });
    $(el).removeAttr('disabled').empty().append(optionData);
  };

  callForStateList = (value_occupation,parentEl) => {
    $.get({
      beforeSend: activateLoader(parentEl),
      url: "https://oasispet.gsa.gov/cpet/cpetPricingTool/stateList?sSocCode="+value_occupation,
      success: (res) => {
        deactivateLoader();
        createStateOptions('#selectState', res);        
      }
    });
  };

  getLACTTitle = (el) => {        
    const value_occupation = $(el).val();
    console.log(value_occupation);
    if (value_occupation != "") {
      $.get({
        beforeSend: activateLoader(el),
        url: "https://oasispet.gsa.gov/cpet/cpetPricingTool/lcatTitle?sSocCode="+value_occupation,
        success: (res) => {
          deactivateLoader();
          $('#fldLcatTitle').val(res.lcatName);
          $('#fldLcatValue').val(res.lcatId);
          callForStateList(value_occupation,el);
          createEANDQLevel(res.lcatId);
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
    $.get({
      beforeSend: activateLoader(el),
      url: "https://oasispet.gsa.gov/cpet/cpetPricingTool/generateMsaWages",
      data: {
        "cpetId": primary_form_data['cpetId'],
        "sEQLevel": secondary_form_data['eqLevel'],
        "sMsa": secondary_form_data['msa'],
        "sSocCode": secondary_form_data['socCode'],
        "sWageScale": secondary_form_data['radioWageScaleOption'],
        "sMarkupPercent": secondary_form_data['markupPercent'],
        "IndirectRateLevelDisplay": secondary_form_data['IndirectRateLevelDisplay'],
        "sEstimateHours1": secondary_form_data['estimatedHours1'],
        "sEstimateHours2": secondary_form_data['estimatedHours2'],
        "sEstimateHours3": secondary_form_data['estimatedHours3'],
        "sEstimateHours4": secondary_form_data['estimatedHours4'],
        "sEstimateHours5": secondary_form_data['estimatedHours5'],
      },
      success: (res) => {
        console.log(res);
        deactivateLoader();
        trdata = "<tr>";
        trdata += "<td>" + res.titleSoc + "</td>";
        trdata += "<td>" + res.eqLcatTile + "</td>";
        trdata += "<td>" + res.stateMsa + "</td>";
        trdata += "<td>" + res.hoursEstimate + "</td>";
        trdata += "<td>$" + res.estHourlyRate + "</td>";
        trdata += "<td>$" + res.totalEstAmount + "</td>";
        trdata += "<tr>";
        $('.bls_result_tbody').empty().append(trdata)
        $('.bls_result').show();
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
  validateSecondary = (form_el) => {
    secondary_data = $(form_el).serializeArray();
    launchResult($('.get_result_btn'));
    return false;
  };
});
