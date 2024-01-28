$(function(){

/** BORA-JS **/

  const ctx = document.getElementById('myChart');


  var chart = new Chart(ctx, {
		type : 'line',
		data : {
			labels : [],
			datasets : [
					{
						data : [],
						label : "Coordinates",
						borderColor : "#3cba9f",
						fill : false
					}]
		},
		options : {
			title : {
				display : true,
				text : 'Chart JS Line Chart Example'
			}
		}
	});

var newData;
var label;

var intervalId = window.setInterval(function(){
  // call your function here
  $.ajax({
        url: "http://ipepdvcompute1.ipe.kit.edu:5618/coord/get-data/",
        type: "GET",
        crossDomain: true,
        success: function (response) {
            console.log(response);
            console.log(response.value.split(" ")[0]);
            newData = response.value.split(" ")[0];
            chart.data.labels.push(response.time);
            chart.data.datasets.forEach((dataset) => {
                dataset.data.push(newData);
            });
            chart.update();
        },
        error: function (xhr, status) {
            console.log("error");
        }
  });
}, 5000);





});
