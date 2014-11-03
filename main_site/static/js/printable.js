(function($) {
    $.QueryString = (function(a) {
        if (a == "") return {};
        var b = {};
        for (var i = 0; i < a.length; ++i)
        {
            var p=a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.search.substr(1).split('&'))
})(jQuery);

(function() {
var Title;

Title = function(args) {
	var self = this;
	self.mvCompany = args.mvCompany;
	self.mvTitle = args.mvTitle;
	self.mvGenre = args.mvGenre;
	self.mvStatus = args.mvStatus;
	self.mvDescription = args.mvDescription, 
	self.mvCount = args.mvCount;
	self.imdbSearch = "http://www.imdb.com/find?q=" + encodeURIComponent(self.mvTitle);
};

printerModel = function () {
	var self = this;
	self.selectedSort = ko.observable('Company');
	self.ascendingDescending = ko.observable('a');
	self.selectedSearch = ko.observable('Title');
	self.searchTerm = ko.observable('');
	self.currentPage = ko.observable(1);
	self.isHotList = ko.observable(false);
	self.loadingResults = ko.observable(false);
	self.loadedTitles = ko.observableArray();
	self.resultsPerPage = ko.observable(20);
	
	self.loadTitles = function() {
		self.loadingResults(true);
		ajaxParams = {
			url: loadTitlesURL,
			type: 'GET', 
			data: {
				currentPage: self.currentPage(),
				isHotList: self.isHotList(),
				orderby: self.selectedSort(),
				ascending: self.ascendingDescending(),
				selectedSearch: self.selectedSearch(),
				searchTerm: self.searchTerm(),
				resultsPerPage: self.resultsPerPage()
			},
			success: self.titleCallback,
			error: self.titleCallbackError
		};
		return $.ajax(ajaxParams);
	};

	self.titleCallback = function(response) {
		var titles, title;
		titles = response.titles;
		self.loadedTitles([]);
		var newTitles = ko.utils.arrayMap(titles, function(item) {
			return new Title(item);
		});
		self.loadedTitles.push.apply(self.loadedTitles, newTitles);		
		self.loadingResults(false);
	};

	self.titleCallbackError = function(response) {
		self.loadedTitles([]);
		self.loadingResults(false);
	};
	
	self.loadParams = function() {
		self.currentPage($.QueryString["currentPage"]);
		self.isHotList($.QueryString["isHotList"]);
		self.selectedSort($.QueryString["orderby"]);
		self.ascendingDescending($.QueryString["ascending"]);
		self.selectedSearch($.QueryString["selectedSearch"]);
		self.searchTerm($.QueryString["searchTerm"]);
		self.resultsPerPage(parseInt($.QueryString["resultsPerPage"]));
		self.loadTitles();
	};
};
}).call(this);