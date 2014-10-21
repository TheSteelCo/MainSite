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

dataViewModel = function (_super) {
	var self = this;
	self.categories = ko.observableArray(['Company', 'Title', 'Genre', 'Status']);
	self.selectedSort = ko.observable('Title');
	self.ascendingDescending = ko.observable('a');
	self.selectedSearch = ko.observable('Title');
	self.searchTerm = ko.observable('');
	self.currentPage = ko.observable(1);
	self.numberOfResults = ko.observable(183);
	self.isHotList = ko.observable(false);
	self.maxPages = ko.computed(function() {
		return Math.ceil(self.numberOfResults() / 20);
	});
	self.loadedTitles = ko.observableArray();
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
		var begin = ((self.currentPage() - 1) * 20) + 1;
		var end = self.currentPage() * 20;
		if (end > self.numberOfResults())
			end = self.numberOfResults();
		return 'Showing ' + begin + '-' + end + ' of ' + self.numberOfResults() + ' results'; 
	})
	self.categoryClicked = function(category) {
		if (category === self.selectedSort())
			self.toggleAscDesc();
		else
			self.ascendingDescending('a');
			self.selectedSort(category);
	}

	self.toggleAscDesc = function() {
		if (self.ascendingDescending() === 'a')
			self.ascendingDescending('d');
		else
			self.ascendingDescending('a');
	}

	self.setPage = function(page) {
		console.log(page);
		if (page >= 1 && page <= self.maxPages())
			self.currentPage(parseInt(page));
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
		console.log('Search on category: ' + self.selectedSearch() + ' - ' + self.searchTerm());
		console.log('I swear theres going to be a search here');
	}

	self.setHotList = function(isHotList) {
		self.isHotList(isHotList);
	}

	self.loadTitles = function() {
		ajaxParams = {
			url: loadTitlesURL,
			type: 'GET', 
			data: {
				currentPage: self.currentPage(),
				isHotList: self.isHotList(),
				orderby: self.selectedSort(),
				ascending: self.ascendingDescending(),
				selectedSearch: self.selectedSearch(),
				searchTerm: self.searchTerm()
			},
			success: self.titleCallback
		};
		return $.ajax(ajaxParams);
	};
	self.titleCallback = function(response) {
		console.log(response);
		var titles, title;
		titles = response.titles;
		self.loadedTitles([]);
		for(i = 0; i < titles.length; i++){
			title = new Title(titles[i]);
			self.loadedTitles.push(Title(title));
		}
		self.numberOfResults(titles.length);
	}
	self.loadTitles();
};
}).call(this);