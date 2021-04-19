/*
	jQuery autoComplete v1.0.7
    Copyright (c) 2014 Simon Steinberger / Pixabay
    GitHub: https://github.com/Pixabay/jQuery-autoComplete
	License: http://www.opensource.org/licenses/mit-license.php
*/

(function($){
    $.fn.autoComplete = function(options){
        var o = $.extend({}, $.fn.autoComplete.defaults, options);

        // public methods
        if (typeof options == 'string') {
            this.each(function(){
                var that = $(this);
                if (options == 'destroy') {
                    $(window).off('resize.autocomplete', that.updateSC);
                    that.off('blur.autocomplete focus.autocomplete keydown.autocomplete keyup.autocomplete');
                    if (that.data('autocomplete'))
                        that.attr('autocomplete', that.data('autocomplete'));
                    else
                        that.removeAttr('autocomplete');
                    $(that.data('sc')).remove();
                    that.removeData('sc').removeData('autocomplete');
                }
            });
            return this;
        }

        return this.each(function(){
            var that = $(this);
            // sc = 'suggestions container'
            that.sc = $(`
              <div class="${o.class} ${o.menuClass} animated pulse faster">
                ${function () {
                  if (o.searchbar) {
                    return `
                    <div style="display: block;overflow: hidden;">
                    <div class="float-right pr-3 pt-3 pb-3 mb-1">
                        <a class="text-primary _search__view_all_link">View all results</a>
                    </div>
                    </div>
                    `
                  }else{
                    return ``
                  }
                }()}
              </div>
            `);
            that.data('sc', that.sc).data('autocomplete', that.attr('autocomplete'));
            that.attr('autocomplete', 'off');
            that.cache = {};
            that.last_val = '';

            function set_view_all_url(term) {
              $('._search__view_all_link').attr('href', `${search_url()}?q=${encodeURIComponent(term)}&page=1`)
            }

            that.updateSC = function(resize, next){
                that.sc.css({
                    maxHeight: o.searchbar? '400px' : that.sc.css('maxHeight'),
                    top: o.searchbar? '53px' : o.top,
                    left: o.searchbar? ($('#searchFrm1').css('display') != 'none'? that.offset().left : that.offset().left) : '0px',
                    width: o.searchbar? ($('#searchFrm1').css('display') != 'none'? that.parent().outerWidth()+50 : '100%') : that.outerWidth()
                });
                if (!resize) {
                    that.sc.show();
                    if (!that.sc.maxHeight) that.sc.maxHeight = parseInt(that.sc.css('max-height'));
                    if (!that.sc.suggestionHeight) that.sc.suggestionHeight = $(`.${o.itemClass}`, that.sc).first().outerHeight();
                    if (that.sc.suggestionHeight)
                        if (!next) that.sc.scrollTop(0);
                        else {
                            var scrTop = that.sc.scrollTop(), selTop = next.offset().top - that.sc.offset().top;
                            if (selTop + that.sc.suggestionHeight - that.sc.maxHeight > 0)
                                that.sc.scrollTop(selTop + that.sc.suggestionHeight + scrTop - that.sc.maxHeight);
                            else if (selTop < 0)
                                that.sc.scrollTop(selTop + scrTop);
                        }
                }
            }
            $(window).on('resize.autocomplete', that.updateSC);

            $(that.sc).insertAfter(that);

            that.sc.on('mouseleave', `.${o.itemClass}`, function (){
                $(`.${o.itemClass}.selected`).removeClass('selected');
            });

            that.sc.on('mouseenter', `.${o.itemClass}`, function (){
                $(`.${o.itemClass}.selected`).removeClass('selected');
                $(this).addClass('selected');
            });

            that.sc.on('mousedown click', `.${o.itemClass}`, function (e){
                var item = $(this), v = item.data('val');
                if (v || item.hasClass(o.itemClass)) { // else outside click
                    that.val(v);
                    set_view_all_url(v)
                    o.onSelect(e, v, item);
                    // that.sc.hide();
                }
                return false;
            });

            that.on('blur.autocomplete', function(){
                try { over_sb = $(`.${o.class}:hover`).length; } catch(e){ over_sb = 0; } // IE7 fix :hover
                if (!over_sb) {
                    that.last_val = that.val();
                    set_view_all_url(that.val())
                    that.sc.hide();
                    setTimeout(function(){ that.sc.hide(); }, 350); // hide suggestions on fast input
                } else if (!that.is(':focus')) setTimeout(function(){ that.focus(); }, 20);
            });

            if (!o.minChars) that.on('focus.autocomplete', function(){ that.last_val = '\n'; that.trigger('keyup.autocomplete'); });

            function suggest(data, searchbar=false){
                setTimeout(function () {
                  var val = that.val();
                  set_view_all_url(val)
                  that.cache[val] = data;
                  // console.log(that.cache);
                  // if (searchbar) {
                  //   $('#searchFrm1 input').attr('style','border-radius: 15px 0px 0px 0px !important')
                  //   $('#searchFrm1 button').css('border-radius', '0px 15px 0px 0px')
                  // }
                  if (data.length && val.length >= o.minChars) {
                      that.sc.find('._sugg_item').remove()
                      for (var i=0;i<data.length;i++){
                        s = $(o.renderItem(data[i], val))
                        s.addClass('_sugg_item')
                        that.sc.append(s);
                      }
                      that.updateSC(0);
                  }
                  else
                      that.sc.hide();
                },10)
            }

            that.on('keydown.autocomplete', function(e){
                // down (40), up (38)
                if ((e.which == 40 || e.which == 38) && that.sc.html()) {
                    var next, sel = $(`.${o.itemClass}.selected`, that.sc);
                    if (!sel.length) {
                        next = (e.which == 40) ? $(`.${o.itemClass}`, that.sc).first() : $(`.${o.itemClass}`, that.sc).last();
                        that.val(next.addClass('selected').data('val'));
                        set_view_all_url(that.val())
                    } else {
                        next = (e.which == 40) ? sel.next(`.${o.itemClass}`) : sel.prev(`.${o.itemClass}`);
                        if (next.length) { sel.removeClass('selected'); that.val(next.addClass('selected').data('val')); set_view_all_url(that.val()) }
                        else { sel.removeClass('selected'); that.val(that.last_val); next = 0; set_view_all_url(that.val()) }
                    }
                    that.updateSC(0, next);
                    return false;
                }
                // esc
                else if (e.which == 27){
                  that.val(that.last_val).sc.hide();
                  set_view_all_url(that.val())
                }
                // enter or tab
                else if (e.which == 13 || e.which == 9) {
                    var sel = $(`.${o.itemClass}.selected`, that.sc);
                    if (sel.length && that.sc.is(':visible')) { o.onSelect(e, sel.data('val'), sel); setTimeout(function(){ that.sc.hide(); }, 20); }
                }
            });

            that.on('focus',function (e) {
              var val = that.val();
              set_view_all_url(val)
              if (val.length >= o.minChars) {
                that.last_val = val;
                clearTimeout(that.timer);
                if (o.cache) {
                    if (val in that.cache) { suggest(that.cache[val]); return; }
                    for (var i=1; i<val.length-o.minChars; i++) {
                        var part = val.slice(0, val.length-i);
                        if (part in that.cache && !that.cache[part].length) { suggest([]); return; }
                    }
                }
                that.timer = setTimeout(function(){ o.source(val, suggest) }, o.delay);
              } else {
                  that.last_val = val;
                  that.sc.hide();
              }
            })

            that.on('keyup.autocomplete', function(e){
                if (!~$.inArray(e.which, [13, 27, 35, 36, 37, 38, 39, 40])) {
                    var val = that.val();
                    set_view_all_url(val)
                    if (val.length >= o.minChars) {
                        if (val != that.last_val) {
                            that.last_val = val;
                            clearTimeout(that.timer);
                            if (o.cache) {
                                if (val in that.cache) { suggest(that.cache[val]); return; }
                                // no requests if previous suggestions were empty
                                for (var i=1; i<val.length-o.minChars; i++) {
                                    var part = val.slice(0, val.length-i);
                                    if (part in that.cache && !that.cache[part].length) { suggest([]); return; }
                                }
                            }
                            that.timer = setTimeout(function(){ o.source(val, suggest) }, o.delay);
                        }
                    } else {
                        that.last_val = val;
                        that.sc.hide();
                    }
                }
            });
        });
    }

    $.fn.autoComplete.defaults = {
        source: 0,
        minChars: 3,
        delay: 150,
        cache: 1,
        class:'autocomplete-suggestions',
        itemClass:'autocomplete-suggestion',
        searchbar:false,
        top:'45px',
        menuClass: '',
        renderItem: function (item, search){
            // escape special characters
            search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
            return `<div class="${$.fn.autoComplete.defaults.itemClass}" data-val="${item}">` + item.replace(re, "<b>$1</b>") + '</div>';
        },
        onSelect: function(e, term, item){},
    };
}(jQuery));
