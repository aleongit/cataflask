'use strict';

//https://gasparesganga.com/labs/jquery-loading-overlay/#examples
const spinner_apren = () => {

  /*
  // Show full page LoadingOverlay
  $.LoadingOverlay("show");
  
  // Hide it after 3 seconds
  setTimeout(function(){
      $.LoadingOverlay("hide");
  }, 3000);
  */

  /*
  // Text
  $.LoadingOverlay("show", {
      image       : "",
      text        : "Loading..."
  });
  */

  $.LoadingOverlay("show", {
    text                    : "Aprenent paraula !",
    image                   : "",
    background              : "rgba(255, 255, 255, 0.8)",        // String
    textAnimation           : "",          // String/Boolean
    textAutoResize          : false,       // Boolean
    textResizeFactor        : 0.5,         // Float
    textColor               : "#202020",   // String/Boolean
    textClass               : "",          // String/Boolean
    textOrder               : 2 ,          // Integer
    // Sizing
    size                    : 50,          // Float/String/Boolean
    minSize                 : 20,          // Integer/String
    maxSize                 : 120,         // Integer/String
    // Misc
    direction               : "column",    // String
    fade                    : [400, 200],  // Array/Boolean/Integer/String
    resizeInterval          : 50,          // Integer
    zIndex                  : 2147483647,  // Integer
  });

  setTimeout(function() {
  //$.LoadingOverlay( "text", "Yep, still loading...");
  $.LoadingOverlay( "text", "Encara aprenent paraula...");
  
    setTimeout(function() {
      $.LoadingOverlay( "text", "Sí sí! Encara aprenent paraula...");

    }, 4500);

  }, 4500);

}

const spinner_load = () => {

  // Show full page LoadingOverlay
  $.LoadingOverlay("show");
  
  /*
  // Hide it after 3 seconds
  setTimeout(function(){
      $.LoadingOverlay("hide");
  }, 3000);
  */

}

//jquery ________________________________________________________
$(document).ready( () => {
    console.log("jQuery ready");
    
    $('#buto_apren').click ( () => { spinner_apren(); });

    $('.apren_cat').click ( () => { spinner_load(); });

    $("a.confirm").BootConfirm({
        complete:function(){
          alert('Confirmed')
        }
      });
      


})


