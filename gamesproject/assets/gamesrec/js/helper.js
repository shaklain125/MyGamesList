function Toast(type, css, msg) {
    if (css == "tl") {
      css = "toast-top-left"
    }else if (css == "tr") {
      css = "toast-top-right"
    }else if (css == "bl") {
      css = "toast-bottom-left"
    }else if (css == "br"){
      css = "toast-bottom-right"
    }else if (css == "b") {
      css = "toast-bottom-full-width"
    }else if (css == "t") {
      css = "toast-top-full-width"
    }else if (css == "tc") {
      css = "toast-top-center"
    }else if (css == "bc") {
      css = "toast-bottom-center"
    }
    this.type = type;
    this.css = css;
    this.msg = msg
    this.closebtn = false
    this.progressbar = false
    this.onclick = null

    this.newestontop = false
    this.preventduplicates = false

    this.showduration = 300
    this.hideduration = 1000

    this.timeout = 5000
    this.extendedtimeout = 1000

    this.show = function() {
      toastr.options = {
        showDuration : this.showduration,
        hideDuration : this.showduration,
        timeOut : this.timeout,//1000;
        extendedTimeOut : this.extendedtimeout, //0
        newestOnTop : this.newestontop,
        preventDuplicates : this.preventduplicates,
        positionClass : this.css,
        progressBar : this.progressbar,
        closeButton : this.closebtn,
        onclick : this.onclick,
      }
      toastr[this.type](this.msg);
    }
}

function rnd(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

function addzero(numb) {
  if (parseInt(numb) < 10)
  {
    return '0' + numb
  }
  return numb
}

function clearToasts() {
  toastr.remove()
  toastr.clear()
}

function epoch_to_datestr(timestamp) {
  var date = new Date(parseInt(timestamp) * 1000)
  return date.getFullYear() + '-' + (date.getMonth()+1) + '-' + date.getDate()
}

function epoch_to_date_obj(timestamp) {
  var date = new Date(parseInt(timestamp) * 1000)
  var d = {
    date: date.getDate(),
    month: (date.getMonth()+1),
    year: date.getFullYear(),
  }
  return d
}

async function imageExists(imageUrl, timeout_time=10000) {
  var timeout = false
  var imageData = new Image();
  return new Promise(function (resolve) {
    imageData.onload = function() {
      if (!timeout) {
        timeout = true
        resolve(true)
      }
    };
    imageData.onerror = function() {
      if (!timeout) {
        timeout = true
        resolve(false)
      }
    };
    imageData.src = imageUrl;
    setTimeout(function () {
      if (!timeout) {
        timeout = true
        imageData.src = ''
        resolve(false)
      }
    },timeout_time)
  })
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function toUpper(str) {
    return str? str.toUpperCase(): ''
}

function toLower(str) {
    return str? str.toLowerCase() : ''
}


function pretty_largenumber_commas(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function century_year() {
  const round = (n, to) => n - n % to;
  return round((new Date()).getFullYear(), 100)
}

function roman_to_Int(str1) {
  if (str1 == null)
  {
    return -1
  }else {

    var ch_get = function (c) {
      var ch = {
        i: 1,
        v: 5,
        x: 10,
        l: 50,
        c: 100,
        d: 500,
        m: 1000,
      }
      return toLower(c) in ch? ch[toLower(c)] : -1
    }

    var num = ch_get(str1.charAt(0));
    var pre, curr;

    for (var i = 1; i < str1.length; i++) {
      curr = ch_get(str1.charAt(i))
      pre = ch_get(str1.charAt(i - 1))
      if(curr <= pre) {
        num += curr;
      }else{
        num = num - pre * 2 + curr;
      }
    }

    return num;
  }
}

function LAX_SETUP() {
  lax.setup()
  const updateLax = () => {
    lax.update(window.scrollY)
    window.requestAnimationFrame(updateLax)
  }
  window.requestAnimationFrame(updateLax)
}

function promise(callback) {
  return new Promise((resolve,reject) => setTimeout(function () {
    callback(resolve,reject)
  },0))
}

async function async_func(callback) {
  await promise(function (resolve,reject) {
    callback()
    resolve()
  })
}

function removeFromArr(val, arr) {
  if (arr.indexOf(val) > -1) {
    arr.splice(arr.indexOf(val), 1)
    return val
  }else {
    return -1
  }
};


function get_platform_icon(platform,ser, p_icons_obj) {
  var p_icons = {
    pc: `<i class="platforms platforms_pc"></i>`,
    playstation: `<i class="platforms platforms_playstation"></i>`,
    xbox: `<i class="platforms platforms_xbox"></i>`,
    nintendo: `<i class="platforms platforms_nintendo"></i>`,
  }
  var found = null
  for (var sr of ser) {
    if (toLower(platform['name']).includes(sr)) {
      found = sr
      if (sr == 'switch') {
        found = 'nintendo'
      }
      break
    }
  }
  if (ser.length > 0 && found && ser.includes(found)) {
    found = removeFromArr(found,ser)
    p_icons_obj[Object.keys(p_icons).indexOf(found)] = p_icons[found]
  }
}

function add_p_icons(p_icons_obj, callback) {
  var p_icons = {
    pc: `<i class="platforms platforms_pc"></i>`,
    playstation: `<i class="platforms platforms_playstation"></i>`,
    xbox: `<i class="platforms platforms_xbox"></i>`,
    nintendo: `<i class="platforms platforms_nintendo"></i>`,
  }
  for (var p_ind = 0; p_ind < Object.keys(p_icons).length; p_ind++) {
    if (Object.keys(p_icons_obj).includes(p_ind.toString())) {
      callback(p_ind, p_icons_obj[p_ind])
    }
  }
}

function shortMonthDateFormat_epoch(e) {
  let m_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  let d = epoch_to_date_obj(e)
  return `${m_short[d.month-1]} ${d.date}, ${d.year}`
}


function set_star_rating(id, val) {
  // $(id).rate({
  //   max_value: 5,
  //   step_size: 0.1,
  //   selected_symbol_type: 'fontawesome_star',
  //   initial_value: val,
  //   readonly: true,
  // });
}

function set_star_rating_fa(id, val) {
  $(id).css('width',`${(val/10)*100}%`)
}

function get_spinner(prop, el) {
  var spinner = null
  if (!prop['classes'])
  {
      prop['classes'] = ''
  }
  if (!prop['styles'])
  {
      prop['styles'] = ''
  }
  spinner = $(`<div id="${prop['id']}" class="spinner-parent d-flex p-2 justify-content-center" style="width:${el.width()}px;top:0px; ${prop['styles']}">
  </div>`)
  var default_spinner = $(`<div class="spinner-border mx-auto" role="status">
    <span class="sr-only">Loading...</span>
  </div>`)
  spinner.append(default_spinner)
  return spinner
}

function set_spinner(prop,el) {
  $(el).append(get_spinner(prop,$(el)))
}

$.fn.dictEach = function (callback) {
  var dict1 = $(this)[0]
  for (var key in dict1)
  {
    callback(key,dict1[key])
  }
  return dict1
}

dict = {
  copy: function (d) {
    return Object.assign({},$(d)[0])
  },
  setChild: function (d,keys,val) {
    function rec_set(d,keys,val,c=-1) {
      if (c == -1) {
        if (keys.length == 1)
        {
          d[keys[0]] = val
          return
        }
        // var laz = dict.copy(brk['lazy'])
        //
        // var ln = dict.copy(laz['loadPrevNextAmount'])
        //
        // var id = dict.copy(ln['id'])
        //
        // id['id3'] = {
        //   id2:slide_no[i]
        // }
        //
        // ln['id'] = id
        //
        // laz['loadPrevNextAmount'] = ln
        //
        // brk['lazy'] = laz
        var first = dict.copy(d[keys[0]]);
        d[keys[0]] = rec_set(first,keys, val, 1)
      }else {
        if (c < keys.length)
        {
          var dict_key_obj = dict.copy(d[keys[c]])
          d[keys[c]] = rec_set(dict_key_obj,keys,val,c+1)
          return d
        }else {
          d = val
          return d
        }
      }
    }
    return rec_set(d,keys,val)
  },
  set : function (dict, o_key, val) {
    dict[o_key] = val
  },
  setAll : function (dict, upd) {
    for (var i in upd) {
      dict[i] = upd[i]
    }
  }
}

function getUrlParameter(url, parameter) {
    parameter = parameter.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?|&]' + parameter.toLowerCase() + '=([^&#]*)');
    var results = regex.exec('?' + url.toLowerCase().split('?')[1]);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

function json_to_params(j) {
  return '?' + Object.keys(j).map(function(k) {
    return encodeURIComponent(k) + '=' + encodeURIComponent(j[k]).replace(/%2C/g,",")
  }).join('&')
}

function params_to_json() {
  var s = decodeURI(location.search.substring(1)).replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g,'":"')
  if (s) {
    return JSON.parse(`{"${s}"}`)
  }else {
    return {}
  }
}

function decodeurl_obj(obj) {
  for (var [key, value] of Object.entries(obj)) {
    obj[key] = decodeURIComponent(value)
  }
  return obj
}

function isInt(n) {
  return Number(n) === n && n % 1 === 0;
}

function isFloat(n) {
  return Number(n) === n && n % 1 !== 0;
}


function prefetch_urls(ignore=null) {
  options = {origins: [],timeout: 4000}
  options['ignores'] = []
  if(ignore){
    options['ignores'].push(ignore)
  }
  options['ignores'].push(new RegExp('logout.*'))

  options['ignores'].push(function () {
    return window.location.pathname.includes('/media')
  })

  options['ignores'].push(function () {
    return window.location.pathname.includes('gameslist')
  })

  options['ignores'].push(function () {
    return window.location.pathname.includes('/profile')
  })

  options['ignores'].push(function () {
    return window.location.pathname.match(new RegExp('reviews.*')) != null
  })

  options['ignores'].push(function () {
    return window.location.pathname.match(new RegExp('recs')) != null
  })

  options['ignores'].push(function () {
    return window.location.pathname.match(new RegExp('write_review.*')) != null
  })

  options['ignores'].push(function () {
    return window.location.pathname.match(new RegExp('account.*')) != null
  })

  // options['ignores'].push(function () {
  //   return window.location.pathname.match(new RegExp('/search.*')) != null
  // })

  // options['ignores'].push(function () {
  //   return window.location.pathname.includes('/search')
  // })

  // options['ignores'].push(new RegExp('search.*'))
  quicklink.listen(options);
}

function catch_search_url_regex() {
  return new RegExp('search\?.*')
}

function prefetch_url(url) {
  if (window.location.pathname.match(new RegExp('reviews.*')) != null || window.location.pathname.match(new RegExp('recs')) != null || window.location.pathname.match(new RegExp('account.*')) != null) {
    return
  }
  quicklink.prefetch(url);
}

function Load_page_async(callback) {
  var l = async function (callback) {
    return await setTimeout(function () {
      callback()
    },1)
  }
  l(callback)
}

function key_with_highest_val(obj) {
  return Object.keys(obj).reduce(function(a, b) {
    return obj[a] > obj[b] ? a : b
  })
}

function onBreakpoint(callback) {
  $(window).on('new.bs.breakpoint',function (e) {
    var breakpoints = {xSmall:1,small:2,medium:3,large:4}
    e.breakpoint = breakpoints[e.breakpoint]
    callback(e)
  })
}

function getBreakpoint() {
  var breakpoints = {xSmall:1,small:2,medium:3,large:4, xLarge:5}
  return breakpoints[bsBreakpoints.detectBreakpoint()]
}

function fillArray(value, len) {
  if (len == 0) return [];
  var a = [value];
  while (a.length * 2 <= len) a = a.concat(a);
  if (a.length < len) a = a.concat(a.slice(0, len - a.length));
  return a;
}

function swap_obj_keys_value(obj){
  var ret = {};
  for(var key in obj){
    ret[obj[key]] = key;
  }
  return ret;
}


function set_trailers_dynamic_btn(btn, trailers_id, igdb, rawg, callback) {
  // console.log(igdb['name']);
  $(btn).on('click', function () {
    if ($(`${trailers_id} a`).length > 0) {
      $(`${trailers_id} a`)[0].click()
    }
  })

  var len_videos = 0

  $(trailers_id).append(function () {
    var videos = igdb.videos ? igdb.videos : []
    var videos_arr = []
    var t_yt_ids = []
    var sub_html = `data-sub-html=\"<h4>${igdb['name']} ${igdb['first_release_date']?`(${epoch_to_date_obj(igdb['first_release_date']).year})` : ''}</h4>\"`
    for (var video of videos) {
      if (toLower(video['name']).includes('trailer')) {
        t_yt_ids.push(video['video_id'])
        videos_arr.push(`<a href="https://www.youtube.com/watch?v=${video['video_id']}" ${sub_html}></a>`)
      }
    }
    var get_rawg_trailers = function () {
      var r_videos = rawg? (rawg.youtube_videos ? rawg.youtube_videos : []) : []
      var r_videos_arr = []
      for (var r_video of r_videos) {
        if (toLower(r_video['name']).includes('trailer')) {
          // console.log('RAWG_TRAILER', r_video['name']);
          if (r_video['external_id']) {
            if ((t_yt_ids.length == 0) ||(t_yt_ids.length > 0 && !t_yt_ids.includes(r_video['external_id']))) {
              r_videos_arr.push(`<a href="https://www.youtube.com/watch?v=${r_video['external_id']}" ${sub_html}></a>`)
            }
          }
        }
      }
      // console.log(r_videos_arr.length == 0 ?'NO RAWG TRAILERS FOUND ON YT': '');
      return r_videos_arr
    }
    videos_arr = videos_arr.concat(get_rawg_trailers())
    callback(videos_arr)
    len_videos= videos_arr.length
    return videos_arr.length > 0 ? videos_arr.join('') : ''
  })

  lightGallery_preset1(trailers_id, len_videos)
}


function lightGallery_preset1(gallerylist_el_id, len_videos) {
  $(gallerylist_el_id).lightGallery({
    loadYoutubeThumbnail: true,
    youtubeThumbSize: 'default',
    hash:false,
    pager:false,
    share:false,
    zoom: false,
    actualSize:false,
    autoplayControls:false,
    closable:len_videos==1? true:false
  })

  var player = function (index) {
    return $($($('.lg-item')[index]).find('.lg-video')[0]).data('player')
  }

  var pause = function (index) {
    try {
      player(index).pauseVideo()
      // ifr.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', "*");
      // console.log('Paused', index);
    } catch (e) {
      // console.log('Not Paused', index,e);
    } finally {

    }
  }

  var play = function (index) {
    try {
      player(index).playVideo()
      // ifr.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', "*");
      // console.log('Playing', index);
    } catch (e) {
      // console.log('Not Playing', index, e);
    } finally {

    }
  }

  var video_iframe = function (index) {
    var ifr = $($('.lg-item')[index]).find('.lg-video-object')[0]
    var ifr_parent = $(ifr).parents().eq(2)
    return {iframe:ifr, is_current: ifr_parent.hasClass('lg-current'), has_loaded: ifr_parent.hasClass('lg-loaded'), loaded_complete: ifr_parent.hasClass('lg-complete')}
  }

  $(gallerylist_el_id).on('onSlideItemLoad.lg',function (event, index) {
    try {
      player(index).addEventListener('onStateChange',function (e) {
        if (e.data == 0) {
          $(gallerylist_el_id).data('lightGallery').goToNextSlide()
        }
      })
    } catch (e) {

    } finally {

    }
    if(index != 0)
    {
      // console.log('onSlideItemLoad.lg', index, $('.lg-video-object'));
      var ifr = video_iframe(index)
      if (ifr.is_current) {
      }else {
        pause(index)
      }
    }
  })

  $(gallerylist_el_id).on('onAferAppendSlide.lg',function (event, index) {
    if(index != 0)
    {
      // console.log('onSlideItemLoad.lg', index, $('.lg-video-object'));
      var ifr = video_iframe(index)
      if (ifr.is_current && ifr.has_loaded && ifr.loaded_complete) {
        // play(index)
      }else {
        pause(index)
      }
    }
  })

  $(gallerylist_el_id).on('onAfterSlide.lg',function (event, prevIndex, index, fromTouch, fromThumb) {
    // console.log('onAfterSlide.lg',index);
    var ifr = video_iframe(index)
    if (ifr.is_current && ifr.has_loaded && ifr.loaded_complete)
    {
      play(index)
    }else {
      pause(index)
    }
  })

  $(gallerylist_el_id).on('onBeforeSlide.lg',function (event, prevIndex, index, fromTouch, fromThumb) {
    // console.log('onAfterSlide.lg',index);
    var ifr = video_iframe(index)
    pause(index)
  })
  $(gallerylist_el_id).on('onAfterOpen.lg',function (ev) {
    $(document).off('click').on('click',function (e) {
      var target = e.target;
      if (!$(target).is('iframe')) {
        console.log(target);
        $('.lg-video-cont').find('iframe').blur()
      }
    })
  })
}

function filtering_chkbox(selector) {
  $(selector).off('click').on('click',function () {
    var states = {
      include : `<i class="icon fa fa-check"></i>`,
      exclude : `<i class="icon fa fa-times"></i>`,
    }
    var lbl = $(this).next()
    var lbl_c = $(lbl).children()

    lbl_c.remove('i')

    if (lbl.hasClass('include')) {
      this.checked = !this.checked
      lbl.removeClass('p-primary')
      lbl.removeClass('include')
      lbl.prepend(states.exclude)
      lbl.addClass('p-danger-o')
      lbl.addClass('exclude')
      $(this).attr('data-filter','exclude')
    }else {
      if (lbl.hasClass('exclude')) {
        lbl.removeClass('p-danger-o')
        lbl.removeClass('exclude')
        $(this).removeAttr('data-filter')
      }else {
        lbl.prepend(states.include)
        lbl.addClass('p-primary')
        lbl.addClass('include')
        $(this).attr('data-filter','include')
      }
    }
  })
}

function setFilterChk(id,filter=undefined) {
  var states = {
    include : `<i class="icon fa fa-check"></i>`,
    exclude : `<i class="icon fa fa-times"></i>`,
  }
  var el = $(id)[0]
  var lbl = $(el).next()
  var lbl_c = $(lbl).children()
  if (filter == 'include') {
    if (!lbl.hasClass('include')) {
      lbl_c.remove('i')
      if (!lbl.hasClass('exclude')) {
        el.checked = !el.checked
      }
      lbl.removeClass('p-danger-o')
      lbl.removeClass('exclude')
      lbl.prepend(states.include)
      lbl.addClass('p-primary')
      lbl.addClass('include')
      $(el).attr('data-filter','include')
    }
  }else if (filter == 'exclude') {
    if (!lbl.hasClass('exclude')) {
      lbl_c.remove('i')
      if (!lbl.hasClass('include')) {
        el.checked = !el.checked
      }
      // el.checked = !el.checked
      lbl.removeClass('p-primary')
      lbl.removeClass('include')
      lbl.prepend(states.exclude)
      lbl.addClass('p-danger-o')
      lbl.addClass('exclude')
      $(el).attr('data-filter','exclude')
    }
  }else {
    if (lbl.hasClass('exclude') || lbl.hasClass('include')) {
      el.checked = !el.checked
    }
    lbl_c.remove('i')
    lbl.removeClass('p-danger-o')
    lbl.removeClass('exclude')
    lbl.removeClass('p-primary')
    lbl.removeClass('include')
    $(el).removeAttr('data-filter')
  }
}

const unslugify = str => str.replace(/[a-z][a-z]*-?/g, ([f, ...rest]) => f.toUpperCase() + rest.join('').replace('-', ' '))


function theme_highcharts(){
  Highcharts.theme = {
      chart: {
          backgroundColor: 'transparent',
          style: {
              fontFamily: 'inherit'
          },
          plotBorderColor: '#606063'
      },
      title: {
          style: {
              color: 'var(--text-color)',
              textTransform: 'uppercase',
              fontSize: '20px'
          }
      },
      subtitle: {
          style: {
              color: 'var(--text-color)',
              textTransform: 'uppercase'
          }
      },
      credits:{
        enabled:false,
      },
      xAxis: {
          gridLineColor: '#707073',
          labels: {
              style: {
                  color: 'var(--text-color)'
              }
          },
          lineColor: '#707073',
          minorGridLineColor: '#505053',
          tickColor: '#707073',
          title: {
              style: {
                  color: '#A0A0A3'
              }
          }
      },
      yAxis: {
          gridLineColor: '#707073',
          labels: {
              style: {
                  color: 'var(--text-color)'
              }
          },
          lineColor: '#707073',
          minorGridLineColor: '#505053',
          tickColor: '#707073',
          tickWidth: 1,
          title: {
              style: {
                  color: '#A0A0A3'
              }
          }
      },
      tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          style: {
              color: '#F0F0F0'
          }
      },
      plotOptions: {
          series: {
              dataLabels: {
                  color: 'var(--text-color)',
                  textOutline:'0px',
                  style: {
                      fontSize: '13px'
                  }
              },
              marker: {
                  lineColor: '#333'
              }
          },
          boxplot: {
              fillColor: '#505053'
          },
          candlestick: {
              lineColor: 'white'
          },
          errorbar: {
              color: 'white'
          }
      },
      legend: {
          backgroundColor: 'transparent',
          itemStyle: {
              color: 'var(--text-color)'
          },
          itemHoverStyle: {
              color: 'var(--text-color)'
          },
          itemHiddenStyle: {
              color: '#606063'
          },
          title: {
              style: {
                  color: '#C0C0C0'
              }
          }
      },
      labels: {
          style: {
              color: '#707073'
          }
      },
      drilldown: {
          activeAxisLabelStyle: {
              color: '#F0F0F3'
          },
          activeDataLabelStyle: {
              color: '#F0F0F3'
          }
      },
      navigation: {
          buttonOptions: {
              symbolStroke: '#DDDDDD',
              theme: {
                  fill: '#505053'
              }
          }
      },
      // scroll charts
      rangeSelector: {
          buttonTheme: {
              fill: '#505053',
              stroke: '#000000',
              style: {
                  color: '#CCC'
              },
              states: {
                  hover: {
                      fill: '#707073',
                      stroke: '#000000',
                      style: {
                          color: 'white'
                      }
                  },
                  select: {
                      fill: '#000003',
                      stroke: '#000000',
                      style: {
                          color: 'white'
                      }
                  }
              }
          },
          inputBoxBorderColor: '#505053',
          inputStyle: {
              backgroundColor: '#333',
              color: 'silver'
          },
          labelStyle: {
              color: 'silver'
          }
      },
      navigator: {
          handles: {
              backgroundColor: '#666',
              borderColor: '#AAA'
          },
          outlineColor: '#CCC',
          maskFill: 'rgba(255,255,255,0.1)',
          series: {
              color: '#7798BF',
              lineColor: '#A6C7ED'
          },
          xAxis: {
              gridLineColor: '#505053'
          }
      },
      scrollbar: {
          barBackgroundColor: '#808083',
          barBorderColor: '#808083',
          buttonArrowColor: '#CCC',
          buttonBackgroundColor: '#606063',
          buttonBorderColor: '#606063',
          rifleColor: '#FFF',
          trackBackgroundColor: '#404043',
          trackBorderColor: '#404043'
      }
  };
  return Highcharts.theme
}
