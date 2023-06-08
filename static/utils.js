const QUEUE_TIMEOUT = 5000
const DEFAULT_PROFILE_IMAGE = 'https://s3.amazonaws.com/spoonflower/public/design_thumbnails/0204/4896/solid_lt_grey_B5B5B5_shop_thumb.png' // https://www.clker.com/cliparts/u/Q/E/2/c/d/grey-background-facebook-2-th.png


function isNull(obj) {
  return [null, undefined].includes(obj)
}

function getColumnTotal(name) {
    const doms = document.getElementsByName(name)
    const totalDoms = document.getElementsByName(`total-${name}`)
    let total = 0
    doms.forEach(function(dom) {
      total += Number(dom.innerHTML)
    })
    totalDoms.forEach(function(totalDom) {
      totalDom.innerHTML = total
    })
}

function calculatePercentages() {
    const doms = document.getElementsByName('percentage')
    const voteDoms = document.getElementsByName('total-votes')
    const totalDoms = document.getElementsByName(`total-total-votes`)
    let totalVotes = 0
    if (!isNull(totalDoms)) {
      if (totalDoms.length > 0) {
        totalVotes = Number(totalDoms[0].innerHTML)
      }
    }
    const totalPercentageDoms = document.getElementsByName('total-percentage')
    let totalPercentage = 0
    if (totalVotes > 0) {
      doms.forEach(function(dom, d) {
        if (voteDoms[d]) {
          const cellValue = Number(voteDoms[d].getAttribute('data-value'))
          const rowPercentage = 100 * cellValue / totalVotes
          if (!isNull(dom)) {
            dom.innerHTML = rowPercentage
            totalPercentage += rowPercentage
          }
        }
      })
    }
    totalPercentageDoms.forEach(function(totalPercentageDom) {
      if (!isNull(totalPercentageDom)) {
        totalPercentageDom.innerHTML = totalPercentage
      }
    })
}

function calculateTotals() {
    const BASE_NAME = 'sum-columns'
    const columnHeaders = document.getElementsByName(BASE_NAME)
    columnHeaders.forEach(function(col, c) {
      const colName = col.getAttribute('data-target')
      const cellsInCol = document.querySelectorAll(`[data-col=${colName}]`)
      const totalCol = document.getElementById(`total-${colName}`)
      let total = 0
      cellsInCol.forEach(function(cell) {
        let count = Number(cell.innerHTML) || 0
        total += count
      })
      if (totalCol) {
        totalCol.innerHTML = total > 0 ? total : '-'
      }
    })
}

function enqueue_collation(e, callback) {
  const key_input = document.getElementById("rq-key")
  if (e) { e.disabled = true }
  let url = '/reports/enqueue/'
  if (key_input.value) {
      if (key_input.value.length) {
          if (key_input.value.length > 0) {
            url = `/reports/dequeue/${key_input.value}`
            if (e) { e.innerHTML = 'Collating ...' }
          }
      }
  }
  fetch(url)
      .then(response => {
          return response.json()
      }).then(data => {
          document.getElementById("rq-key").value = data.job_key
          let enq = null
          if (![200, 201].includes(data.status)) {
              document.getElementById('rq-result').innerHTML = `please wait...`
              enq = setTimeout(enqueue_collation(e), QUEUE_TIMEOUT)
          } else {
            if (e) {
              e.innerHTML = 'collate results'
              e.disabled = false
            }
            document.getElementById('rq-result').innerHTML = `${data.message}`.toLowerCase() + `!`
            if (callback) {
              clearTimeout(enq)
              callback()
            } else {
              window.location.reload();
            }
          }
          return {
            data: data,
          }
      }).catch(error => {
          console.log(error)
      })
};

function selectZoneID(e) {
  const zone_ct = document.getElementById('id_zone_ct_id')
  const zone = document.getElementById('id_zone_id')
  const zone_list = document.getElementById(`zone_${zone_ct.value}`)
  if (zone_list) {
    zone.innerHTML = zone_list.innerHTML
  }
}

function setPositionTitle() {
  const zone_ct = document.getElementById('id_zone_ct_id')
  const zone = document.getElementById('id_zone_id')
  const title = document.getElementById('id_title')
  const label = document.getElementById('id_title_label')
  let zone_ct_title = zone_ct.options[zone_ct.selectedIndex].text.toLowerCase()
  let zone_title = zone.options[zone.selectedIndex].text
  if (zone_ct_title == 'nation') {
    title.value = `President, ${zone_title}`
  } else {
    title.value = `Parliamentary Representative, ${zone_title} Constituency`
  }
  label.value = title.value
}

function toggleById(domID, show=null) {
  let dom = domID
  if (typeof domID === 'string') {
    dom = document.getElementById(domID)
  }
  const hider = document.getElementById(`${domID}_hide`)
  const shower = document.getElementById(`${domID}_show`)
  if (!isNull(dom)) {
    if (isNull(show)) {
      show = dom.hidden ? true : false
    }
    dom.hidden = !show
    if (!isNull(hider)) {
      hider.hidden = dom.hidden
    }
    if (!isNull(shower)) {
      shower.hidden = !hider.hidden
    }
    if (show) {
      toggleSticky(show)
    }
  }
}

function toggleByName(domName, show=null) {
  const doms = document.getElementsByName(domName)
  doms.forEach(function(dom, d) {
    toggleById(dom, show)
  })
}

function toggleSticky(show=null) {
  const findClass = 'td-sticky'
  const expandClass = 'td-expand'
  const doms = document.querySelectorAll(`.${findClass}`)
  doms.forEach(function(dom, d) {
    if (isNull(show)) {
      if (dom.classList.contains(expandClass)) {
        dom.classList.remove(expandClass)
      } else {
        dom.classList.add(expandClass)
      }
    } else {
      if (show) {
        dom.classList.add(expandClass)
      } else {
        dom.classList.remove(expandClass)
      }
    }
  })

}

function loadImage(dom, URL=null, mode='profile') {
  if (!dom) return false
  if (!URL) {
      if (mode==='profile') {
          dom.src = DEFAULT_PROFILE_IMAGE
      }
      return false
  }
  var tester=new Image();
  tester.onload=() => {
      dom.src = URL
  };
  tester.onerror= () => {
      dom.src = DEFAULT_PROFILE_IMAGE
  };;
  tester.src=URL;
}

function correctImageSrc() {
  const imgs = document.querySelectorAll('img')
  for (img of imgs) {
      loadImage(img, img?.src)
  }
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
      }
  }
  return cookieValue;
}

function populateZones(data, qdom) {
  if (!qdom) return false
  const old_value = qdom.getAttribute('data-value')
  let zoneBaseName = qdom.getAttribute('data-src')
  if (zoneBaseName) {
    zoneBaseName = zoneBaseName
                      .replace('-filter', '')
  }
  const zone = document.getElementById(zoneBaseName)
  const zone_count = document.getElementById(`${zoneBaseName}-count`)
  zone.innerHTML = ''
  const options = data?.data[0]
  if (options.length > 0) {
    let dom = document.createElement('option')
    dom.value = null
    dom.label = `-- ${options.length} options`
    dom.textContent = `-- ${options.length} options`
    zone.appendChild(dom)
    if (zone_count) {
      zone_count.innerHTML = `-- ${options.length} options`
    }
    options.forEach(function(option) {
      let dom = document.createElement('option')
      let value = option?.pk
      dom.value = value
      dom.label = option?.title
      dom.textContent = option?.title
      if (old_value) {
        if (`${value}` === `${old_value}`) {
          dom.selected = true
        }
      }
      zone.appendChild(dom)
    })
  }
}

function fetchZones(qdom, endPoint, callBack) {
  /*
  *  Ensure that qdom has the following
  *
  *  #{base}: select box dom element with id {base}
  *  #{base}-count: div or span dom element with id {base}-count
  *  data-src: attribute = containing the name of the field in the form {base}-filter,
  *  data-value: attribute = containing the old value of the {base} dom
  */

  let q = qdom
  if (typeof qdom === 'object') {
    q = qdom?.value
  }
  let qPair = ''
  if (q.length > 0) {
    qPair = `?q=${q}`
  }

  endPoint = endPoint.toLowerCase()
  const apiUrl = `/api/geo/${endPoint}/choices/` // '{{ zone_choice_api }}'
  const csrftoken = getCookie('csrftoken');
  const FETCH_URL = `${apiUrl}${qPair}`
  const FETCH_CONFIG = {
      method: 'POST',
      credentials: 'same-origin',
      headers:{
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({'post_data': 'Data to post'})
  }
  fetch(FETCH_URL, FETCH_CONFIG,
  ).then(response => {
    return response.json()
  })
  .then(data => callBack(data, qdom))
}

function getDom(dom) {
  if (typeof dom === 'string') {
    dom = document.getElementById(dom)
  }
  return dom
}

function populateOptions(data, destination){
  destination = getDom(destination)
  if (!destination) { return false }

  destination.disabled = false
  destination.innerHTML = ''
  const old_value = destination.getAttribute('data-value')
  const options = data?.data[0]

  if (options.length > 0) {
    let dom = document.createElement('option')
    dom.value = null
    dom.label = `-- ${options.length} options`
    dom.textContent = `-- ${options.length} options`
    destination.appendChild(dom)
    options.forEach(function(option) {
      let dom = document.createElement('option')
      let value = option?.pk
      dom.value = value
      dom.label = option?.title
      dom.textContent = option?.title
      if (old_value) {
        if (`${value}` === `${old_value}`) {
          dom.selected = true
        }
      }
      destination.appendChild(dom)
    })
  }
}

function fetchZonesByLevel(endPoint, destination) {
  if (!endPoint) return false
  if (!destination) return false
  if (typeof endPoint === 'object') {
    endPoint = endPoint.options[endPoint.selectedIndex].textContent
    endPoint = endPoint.toLowerCase()
  } else if (typeof endPoint === 'string') {
    endPoint = endPoint.toLowerCase()
  } else {
    return false;
  }
  
  destination = getDom(destination)
  destination.innerHTML = '<option>-- Loading...<option>'
  destination.disabled = true

  if (['nation', 'region', 'constituency', 'station'].includes(endPoint)) {
    fetchZones({ value: '' },
                endPoint,
                function(data, _) {
                  populateOptions(data, destination)
                })
  } else {
    return false
  }

}


function filterZonesOnForm(dom){
  let ct = document.getElementById('id_zone_ct_id')
  const zones = document.getElementById('id_zone_id')
  if (!ct || !zones) { return false }
  ct = ct.options[ct.selectedIndex].textContent.toLowerCase()
  fetchZones(dom, ct, populateZones)
}


function filterSelect(source, select) {
  if (typeof source == 'string') {
    source = document.getElementById(source)
  }
  if (!source) return false
  if (typeof select == 'string') {
    select = document.getElementById(select)
  }
  if (!select) return false

  if (select.options) {
    Array.from(select.options).forEach(function(option) {
      console.log(option)
      const needle = source.value
      const haystack = option.textContent
      let found = (
        haystack === needle
        || haystack.includes(needle)
      )
      let needlesInHaystack = true
      const pieces = needle.split(' ')
      pieces.forEach(function(piece) {
        needlesInHaystack = needlesInHaystack && haystack.includes(piece)
      })
      found = found || needlesInHaystack
      option.hidden = !found
    })
  }
}
