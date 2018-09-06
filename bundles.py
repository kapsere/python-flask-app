from flask_assets import Bundle

bundles = {

    'main.js': Bundle(
        'js/lib/jquery-3.1.1.min.js',
        'js/lib/bootstrap.min.js',
        'js/lib/flickity.pkgd.min.js',
        'js/lib/jquery.fancybox.min.js',
        'js/main.js',
        output='gen/main.js', filters='jsmin'),
        
    'main.css': Bundle(
        'css/lib/bootstrap.min.css',
        'css/styles-main.css',
        output='gen/main.css', filters='cssmin'),
        
    'blog.css' : Bundle(
        'css/lib/jquery.fancybox.min.css',
        'css/styles-blog.css',
        output ='gen/blog.css', filters='cssmin')
}