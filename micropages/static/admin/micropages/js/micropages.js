/** Maintains a live preview of code being edited. */
var Preview = {
    /** Current delay until preview refresh, in seconds, or null if preview was shown and there were no code changes after that. */
    delay: null,
    /** Timer id. */    
    timer: null,            
    /** Current iframe scroll position. */
    frameScroll: null,

    /** Processes a timer tick. Reduces current delay by a second and related actions. */
    tick: function() {
        if (this.delay !== null) {                    
            this.delay -= 100;
            if (this.delay < 0) {
                this.delay = null;

                // Show preview only if pane is not collapsed.
                if (jQuery('#preview').width() > 0 && Page.autorefresh) {
                    this.reloadPreview();
                }
            }
        }
    },
    
    /** Restarts a delay that will need to elapse before preview will be refreshed. */
    trigger: function() {                
        if (this.delay == null) {
            this.delay = 3000;
        } else {
            // If user is still typing, delay frame reload by at least a second or so, to prevent lost keystrokes.
            if (this.delay < 2000) {
                this.delay = 2000;
            }
        }
    },

    /** Capture scroll position on preview frame. */
    captureScrollPosition: function() {
        var that = this;

        jQuery('#preview-frame').contents().scroll(function () {
            that.frameScroll = jQuery(this).scrollTop();
        });
    },

    /** Restores preview frame scrolling position. */
    restoreScrollPosition: function() {
        if (this.frameScroll !== null) {
            jQuery('#preview-frame').contents().scrollTop(this.frameScroll);
        }        

        this.captureScrollPosition();
    },

    /** Reloads preview. */
    reloadPreview: function() {                
        var text = Page.editor.getSession().getValue();
        jQuery('#preview-form').find('textarea').val(text).parent().submit();
    },

    /** Initializes live preview. */
    setup: function() {
        var that = this;
        
        // Setup scheduler.
        this.timer = setInterval(function() {
            that.tick();
        }, 100);

        // Process iframe reload to restore scroll position, etc.
        jQuery('#preview-frame').load(function() {
            that.restoreScrollPosition();
        });

        // Fire preview load.
        this.reloadPreview();        
    }
}        

/** Various page related functionality. */
var Page = {
    /** Page-wide ACE editor instance. */
    editor: null,
    /** Original Django-generated text area for page content field. */
    djangoEditor: null,
    /** Specifies wether autorefresh is enabled. */
    autorefresh: true,
    /** Modified status. */
    modified: false,

    /** Initializes ACE editor. */
    setupAceEditor: function() {
        // Django generated textarea for the content field.
        this.djangoEditor = jQuery('.form-content textarea');

        // Create ACE editor and setup some dark theme. Yeah, some time later we probably will want a theme selector.        
        this.editor = ace.edit('editor');
        this.editor.setTheme('ace/theme/monokai');
    
        // Enable HTML syntax highlighting.
        var htmlMode = ace.require('ace/mode/html').Mode;
        this.editor.getSession().setMode(new htmlMode());

        this.editor.getSession().setTabSize(4);
        this.editor.getSession().setUseSoftTabs(true);
        this.editor.setHighlightActiveLine(false);
        this.editor.setShowPrintMargin(false);

        var that = this;
        // Make sure that ACE and Django textarea have the same value.
        this.editor.getSession().setValue(this.djangoEditor.val());
        this.editor.getSession().on('change', function() {
            if (!that.modified) {
                that.modified = true;
                jQuery('footer .modified-status').show();
            }

            that.djangoEditor.val(that.editor.getSession().getValue());

            Preview.trigger();
        });

        // Check that path contains a value, before Django validation kicks in and display in BIG RED letters that there is an error.
        jQuery('.submit-row input').click(function(e) {
            var value = jQuery.trim(jQuery('.form-path input').val());
            if (value == '') {
                alert('Path is required');
                e.preventDefault();
            }
        });

        // Show modified message on page exit.
        jQuery(window).bind('beforeunload', function() {
            if (that.modified) {
                return 'Unsaved changes will be lost. Are you sure you want to navigate away from this page?';
            } else {
                return null;
            }
        });

        // If form is actually being submitted, reset modified flag to avoid warning message.
        jQuery('#page_form').submit(function() {
            that.modified = false;
        });
    },

    /** Sets up split panes for editor and preview. */
    setupSplitPanes: function() {
        // Enable split pane between editor and preview.
        jQuery('.content').splitter({
            minLeft: 400,
            minRight: 100,
            dock: 'right',
            dockSpeed: 200,
            cookie: "docksplitter",
            dockKey: 'Z'                
        });

        var lastWidth = null;
        var lastHeight = null;
        jQuery(window).resize(function() {
            var w = window.innerWidth;
            var h = window.innerHeight;
            if (lastWidth != w || lastHeight != h) {
                lastWidth = w;
                lastHeight = h;
                jQuery('.content').trigger('resize');  
            }
        });

        var that = this;
        jQuery('#editor').resize(function() {
            that.editor.resize();
        });
    },

    /** Setup keybindings. */
    setupKeys: function() {
        jQuery.ctrl('S', function() {
            jQuery('input[name=_continue]').click();
        });
    },

    /** Adjust refresh controls style based on the current value of autorefresh flag. */
    adjustRefreshControlsStyle: function() {
        jQuery('.auto-refresh-link').toggleClass('auto-refresh-active', this.autorefresh);        
    },

    /** Setup refresh controls. */
    setupRefreshControls: function() {
        var that = this;
        jQuery('.auto-refresh-link').click(function(e) {
            that.autorefresh = !that.autorefresh;
            that.adjustRefreshControlsStyle();

            e.preventDefault();
        });
        
        jQuery('.refresh-now-link').click(function(e) {
            Preview.reloadPreview();

            e.preventDefault();
        });

        this.adjustRefreshControlsStyle();
    },

    setup: function() {
        this.setupAceEditor();
        this.setupSplitPanes();
        this.setupKeys();
        this.setupRefreshControls();
    }
}

// Initialize the page.
jQuery(document).ready(function() {
    Page.setup();
    Preview.setup();
});