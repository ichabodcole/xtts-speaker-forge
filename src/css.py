def app_css():
    return """
        #header-image { text-align: center; }
        #header-image button { display: flex; justify-content: center; pointer-events: none; }
        #header-image img { max-width: 876px }
        .xtts-header { text-align: center; margin-bottom: -10px; }
        .xtts-header h1 {
            --body-text-color: rgb(103 232 249);
            display: block;
            text-align: center;
            line-height: 0;
            margin: 10px 0 -20px;
            letter-spacing: 0.1em;
        }
        .tab-nav button { font-size: 1.5em; }
        .tab-nav button.selected { --body-text-color: rgb(103 232 249); }
        .processing-text { padding-left: 10px; }
        .section-description { 
            --body-text-color: rgb(103 232 249);
            font-size: 1.1em; 
            margin-top: 5px; 
            margin-left: 5px;
        }
        .changelog-content {
            padding: 0 10px 15px;
            font-size: 1.1em;
        }
        .about-content {
            padding: 0 10px 15px;
            font-size: 1.1em;
        }
        """
