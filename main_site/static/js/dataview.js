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

dataViewModel = function () {
	var self = this;
	self.categories = ko.observableArray(['Company', 'Title', 'Genre', 'Status']);
	self.selectedSort = ko.observable('Company');
	self.ascendingDescending = ko.observable('a');
	self.selectedSearch = ko.observable('Title');
	self.searchTerm = ko.observable('');
	self.currentPage = ko.observable(1);
	self.numberOfResults = ko.observable(0);
	self.isHotList = ko.observable(false);
	self.loadingResults = ko.observable(false);
	self.resultsPerPage = ko.observable(20);
	self.maxPages = ko.computed(function() {
		if (self.resultsPerPage() != 0)
			return Math.ceil(self.numberOfResults() / self.resultsPerPage());
		else
			return 1;
	});
	self.lastResultsPerPage = 20;
	self.loadedTitles = ko.observableArray();
	self.resultsPerPageOptions = ko.observableArray(
		[{count: 20, caption: '20'},
		{count: 50, caption: '50'},
		{count: 100, caption: '100'},
		{count: 200, caption: '200'},
		{count: 0, caption: 'ALL'}
		]
	);
	self.paginationValues = ko.computed(function() {
		var returnPages = [];
		if (self.currentPage() === 1){
			for (var i = 0; i < self.maxPages() && i < 3; i++)
			{
				returnPages.push(self.currentPage() + i);
			}
		}
		else if(self.currentPage() == self.maxPages()){
			var i = self.maxPages() - 2;
			if (i < 1)
				i = 1;
			for (i; i <= self.maxPages(); i++)
			{
				returnPages.push(i);
			}
		}
		else
		{
			returnPages.push(self.currentPage() - 1);
			returnPages.push(self.currentPage());
			returnPages.push(self.currentPage() + 1);
		}
		return returnPages;
	});
	self.resultsText = ko.computed(function() {
		var begin, end;
		if (self.resultsPerPage() != 0)
		{
			begin = ((self.currentPage() - 1) * self.resultsPerPage()) + 1;
			end = self.currentPage() * self.resultsPerPage();
			if (end > self.numberOfResults())
				end = self.numberOfResults();
		}
		else
		{
			begin = 1;
			end = self.numberOfResults();
		}

		return 'Showing ' + begin + '-' + end + ' of ' + self.numberOfResults() + ' results'; 
	})
	self.categoryClicked = function(category) {
		if (category === self.selectedSort())
			self.toggleAscDesc();
		else
			self.ascendingDescending('a');
			self.selectedSort(category);
		self.currentPage(1);
		self.loadTitles();
	}

	self.toggleAscDesc = function() {
		if (self.ascendingDescending() === 'a')
			self.ascendingDescending('d');
		else
			self.ascendingDescending('a');
	}

	self.setPage = function(page) {
		var previousPage = self.currentPage();
		page = parseInt(page)
		if (page != self.currentPage()) {
			if (page >= 1 && page <= self.maxPages()) {
				self.currentPage(parseInt(page));
				self.loadTitles();
			}
		}
	}
	self.incrementPage = function() {
		self.setPage(self.currentPage()+1);
	}
	self.decrementPage = function() {
		self.setPage(self.currentPage()-1);
	}
	self.goToFirstPage = function() {
		self.setPage(1);
	}
	self.goToLastPage = function() {
		self.setPage(self.maxPages());
	}
	self.caretDirection = ko.pureComputed(function() {
		return self.ascendingDescending() === 'a' ? "caret" : "caret caret-reversed";
	}, self);

	self.runSearch = function() {
		self.currentPage(1);
		self.loadTitles();
	}

	self.clearSearch = function() {
		self.currentPage(1);
		self.searchTerm('');
		self.loadTitles();
	}

	self.setHotList = function(isHotList) {
		self.isHotList(isHotList);
		self.loadTitles();
	}

	self.setResultsPerPage = function() {
		if (self.lastResultsPerPage != self.resultsPerPage()) {
			self.lastResultsPerPage = self.resultsPerPage();
			self.currentPage(1);
			self.loadTitles();
		}
	}

	self.loadTitles = function() {
		self.loadingResults(true);
		self.numberOfResults(0);
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
				resultsPerPage: self.resultsPerPage(),
			},
			success: self.titleCallback,
			error: self.titleCallbackError
		};
		return $.ajax(ajaxParams);
	};

	self.printPage = function() {
		data = {currentPage: self.currentPage(),
				isHotList: self.isHotList(),
				orderby: self.selectedSort(),
				ascending: self.ascendingDescending(),
				selectedSearch: self.selectedSearch(),
				searchTerm: self.searchTerm(),
				resultsPerPage: self.resultsPerPage()
			};
		window.open(printPagesURL + '?' + jQuery.param(data));
	}

	self.printAll = function() {
		data = {currentPage: self.currentPage(),
				isHotList: self.isHotList(),
				orderby: self.selectedSort(),
				ascending: self.ascendingDescending(),
				selectedSearch: self.selectedSearch(),
				searchTerm: self.searchTerm(),
				resultsPerPage: 0};
		window.open(printPagesURL + '?' + jQuery.param(data));
	}

	self.titleCallback = function(response) {
		var titles, title;
		titles = response.titles;
		self.loadedTitles([]);
		for(i = 0; i < titles.length; i++){
			title = new Title(titles[i]);
			self.loadedTitles.push(Title(title));
		}
		self.numberOfResults(response.results);
		self.loadingResults(false);
	};

	self.titleCallbackError = function(response) {
		self.loadedTitles([]);
		self.numberOfResults(0);
		self.loadingResults(false);
	};

	
	ko.bindingHandlers.executeOnEnter = {
	    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
	        var allBindings = allBindingsAccessor();
	        $(element).keypress(function (event) {
	            var keyCode = (event.which ? event.which : event.keyCode);
	            if (keyCode === 13) {
	                allBindings.executeOnEnter.call(viewModel);
	                return false;
	            }
	            return true;
	        });
	    }
	};
};
}).call(this);