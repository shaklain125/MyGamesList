(function($) {

	$.fn.readMore = function(options) {

		var defaults = {
			readMoreLinkClass: "read-more__link",
			readMoreText: "Read more",
			readLessText: "Read less",
			readMoreHeight: 150
		};

		options = $.extend(defaults, options);

		var obj = $(this);

		function getRefElementOptions(refElement) {
			this.collapsedHeight = typeof refElement.data("options") !== "undefined" ? refElement.data("options") : options.readMoreHeight;
		}

		obj.each(function() {
			var $target = $(this);
			var refElementOptions = new getRefElementOptions($target);
			$(this).after(`<span>${options.readMoreText}</span>`).next().addClass(options.readMoreLinkClass);
			$(this).css({"height": refElementOptions.collapsedHeight,"overflow": "hidden"});
		});

		$(`.${options.readMoreLinkClass}`).off('click').on('click',function() {
			var $target = $(this).prev();
			var refElementOptions = new getRefElementOptions($target);

			if ($target.css("overflow") === "hidden") {
				$target.css({"height": "auto","overflow": "auto"});
				$target.addClass("expanded");
			}else {
				$target.css({"height": refElementOptions.collapsedHeight,"overflow": "hidden"});
				$target.removeClass("expanded");
			}
			$(this).text($(this).text() === options.readMoreText? options.readLessText : options.readMoreText);
		});
	};

})(jQuery);
