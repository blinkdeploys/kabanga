  
// RESULT APPROVAL

function selectApprovalOffice(opt) {
    const zoneLevel = document.getElementById('zone-level')
    const zone = document.getElementById('zone')
    if (opt?.value.length > 0) {
        let url = `/poll/result_approvals/${opt?.value}/`
        if (zoneLevel?.value?.length > 0) {
        url += `${zoneLevel?.value}/`
        if (zone?.value > 0) {
            url += `${zone?.value}`
        }
        }
        location.href = url
    }
}
    
function selectApprovalZoneLevel(opt) {
    const officeType = document.getElementById('office-type')
    const zone = document.getElementById('zone')
    if (officeType?.value?.length > 0) {
      let url = `/poll/result_approvals/${officeType?.value}/`
      if (opt?.value?.length > 0) {
        url += `${opt?.value}/`
        if (zone?.value > 0) {
          url += `${zone?.value}`
        }
      }
      location.href = url
    }
}
  
function selectApprovalZone(opt) {
    const officeType = document.getElementById('office-type')
    const zoneLevel = document.getElementById('zone-level')
    if (officeType?.value?.length > 0) {
      let url = `/poll/result_approvals/${officeType?.value}/`
      if (zoneLevel?.value?.length > 0) {
        url += `${zoneLevel?.value}/`
        if (opt?.value > 0) {
          url += `${opt?.value}`
        }
      }
      location.href = url
    }
}

function ecSummaryTotalChange() {
    const approval_total_votes_ec_total = document.getElementById('approval_total_votes_ec_total')
    const total_variance_total = document.getElementById('total_variance_total')
    const btn_approves = document.getElementsByName('btn_approve')
    const approval_total_votes_ecs = document.getElementsByName('approval_total_votes_ec')
    const total_variances = document.getElementsByName('total_variance')
    const total_valid_votes = document.getElementsByName('approval_total_valid_votes')
    const approval_certifys = document.getElementsByName('approval_certify')
    const approval_certify_checks = document.getElementsByName('approval_certify_check')
    let sum_ec = 0
    let sum_variance = 0
    for (i=0; i< total_valid_votes.length; i++) {
      if (approval_total_votes_ecs[i]) {
        if (approval_certifys[i]) {
          approval_certifys[i].hidden = approval_total_votes_ecs[i].value <= 0
        }
        if (btn_approves[i] && approval_certify_checks[i]) {
          btn_approves[i].hidden = approval_total_votes_ecs[i].value <= 0 || approval_certify_checks[i].checked === false
        }
        if (total_variances[i] && total_valid_votes[i]) {
          total_variances[i].innerHTML = Number(approval_total_votes_ecs[i].value) - Number(total_valid_votes[i].innerHTML)
        }
        sum_ec += Number(approval_total_votes_ecs[i].value)
        sum_variance += Number(total_variances[i].innerHTML)
      }
    }
    approval_total_votes_ec_total.innerHTML = sum_ec
    total_variance_total.innerHTML = sum_variance
    handleAllRowsChecked()
}
// RESULT APPROVAL


// TABLE GENERAL

function copyById(from, to) {
    if (typeof from === 'string') { from = document.getElementById(from) }
    if (typeof to === 'string') { to = document.getElementById(to) }
    if (from && to) {
      to.value = Number(from.innerHTML)
    }
}

function batchCopyByName(from, to) {
    fromDOMs = document.getElementsByName(from)
    toDOMs = document.getElementsByName(to)
    for (i=0; i<fromDOMs.length; i++) {
      copyById(fromDOMs[i].id, toDOMs[i].id)
    }
    handleAllRowsChecked()
}

function handleAllRowsChecked() {
    const dom = document.getElementById('approval_certify')
    if (dom) {
      dom.hidden = true
      if (allRowsChecked()) {
        dom.hidden = false
      }
    }
}

function allRowsChecked() {
    const doms = document.getElementsByName('row-checks')
    let result = true
    for (dom of doms) {
      result = result && dom.className === 'fa fa-regular fa-circle-check text-success'
    }
    if (result) { return true }
    return false
}

function unCheckRow(id) {
    const check = document.getElementById(id)
    check.className= 'fa fa-regular fa-circle text-danger'
    handleAllRowsChecked()
}

function checkRow(id) {
    const check = document.getElementById(id)
    check.className= 'fa fa-regular fa-circle-check text-success'
    handleAllRowsChecked()
}

function checkAllRows() {
    const doms = document.getElementsByName('row-checks')
    for (dom of doms) {
      checkRow(dom.id)
    }
    checkRow('row-check-all')
}

// TABLE GENERAL
