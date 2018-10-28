
var types = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/types',
    remote: {
      url: '/types?q=%QUERY',
      wildcard: '%QUERY'
    }
  });

$('.type').typeahead(null, {
    name: 'type',
    display: 'value',
    source: types
});


var names = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/names',
    remote: {
      url: '/names?q=%QUERY',
      wildcard: '%QUERY'
    }
  });

$('.name').typeahead(null, {
    name: 'name',
    display: 'value',
    source: names
});