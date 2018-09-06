"use strict";
// Set Active class on carousel slider
function setActiveClassCarousel() { 
var posts = document.querySelectorAll('#posts-slider .carousel-inner .item'),
    comments = document.querySelectorAll('#comments-slider .carousel-inner .item');
//console.log(posts);
//console.log(comments);
if (posts.length >= 1) {
  posts[0].classList.add('active');
  }
if (comments.length >= 1 ) {
  comments[0].classList.add('active');  
  }
}
setActiveClassCarousel();

// Swipe for Bootstrap Carousel 
$(".carousel").on("touchstart", function(event){
        //console.log($(this));
        var xClick = event.originalEvent.touches[0].pageX;
    $(this).one("touchmove", function(event){
        var xMove = event.originalEvent.touches[0].pageX;
        // Adjust sensitivity by adjusting then number
        if( Math.floor(xClick - xMove) > 5 ){
            $(this).carousel('next');
        }
        // Adjust sensitivity by adjusting then number
        else if( Math.floor(xClick - xMove) < -5 ){
            $(this).carousel('prev');
        }
    });
    $(".carousel").on("touchend", function(){
            $(this).off("touchmove");
    });
});
// Flickity Options  
var options = {
  // options
  cellAlign: 'left',
  draggable : false,
  contain: true,
  pageDots: false,
  lazyLoad:true,
  wrapAround:true,
  groupCells:4,
  prevNextButtons: true,
  arrowShape: { 
  x0: 15,
  x1: 60, y1: 50,
  x2: 75, y2: 35,
  x3: 45
}};
// enable prev/next buttons at 768px
if ( matchMedia('screen and (max-width: 768px)').matches ) {
   options.groupCells = false;
   options.lazyLoad=true,
   options.contain=true,
   options.draggable = true;
}
if ($('.main-carousel')) {
$('.main-carousel').flickity(options);
// Flickity container has wrong size when switching tabs bug fix //
$('[href="#following"],[href="#followers"]').on( 'shown.bs.tab', function (e) {
  $('.main-carousel').flickity('resize');
});
}
// init fancybox
$(".gallery").fancybox({
  hideScrollbar : true
});
//Disable FancyBox Gallery History To Prevent messing up the flow of the browser history.
//Back And Forward Browser buttons will ignore Fancybox browse history.	
$.fancybox.defaults.hash = false;	

// add html5 data attribute to fancybox instance to group all images to create gallery
$('.gallery').attr('data-fancybox', 'group');

// create fancybox gallery
if (document.querySelector('.blog-post-content')) {
var images = document.querySelector(".blog-post-content").getElementsByTagName('img');
function makeLink(image){image.outerHTML = '<a target="_blank" class="gallery" data-fancybox="group" href="' + image.src + '">' + image.outerHTML + '</a>';}
for(var i = 0, l = images.length; i < l; ++i){makeLink(images[i]);}
}

// Delete Posts
if (document.querySelector('.delete-post')) {
var postDeleteURL = Flask.url_for('blog.delete_post', {slug : slug}),  
  deletePostBtn = document.querySelector('.delete-post');
deletePostBtn.addEventListener('click',function(){
  document.querySelector('.delete-msg').innerHTML = 'Are you sure you want to delete this post?';
  document.querySelector('.delete-form').outerHTML = `<form class='delete-form' method='post' action=${postDeleteURL}>` + `<button class='btn btn-danger yes-btn'>` + "Yes" + `</button>` + `</form>`;
}); 
}
// Ajax load more comments
if (document.querySelector('.load-more')) {
  $('.load-more').click(function(){
    $.ajax({
      url: Flask.url_for('blog.load_comments', {slug: slug}),
      type : "POST",
      success: function(resp){
        $('.comments-container').append(resp.data);
        $('.load-more').remove().delay( 300 );
        flask_moment_render_all();  
      }
    });
  });
}
