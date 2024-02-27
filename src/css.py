def app_css():
    return """
        #header-image { display: flex; justify-content: center; pointer-events: none; }
        #header-image button { display: flex; justify-content: center; pointer-events: none; }
        #header-image img { max-width: 876px; width: 100%; }
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
        .ui-disabled {
            pointer-events: none;
        }
        .ui-disabled::before {
            content: "";
            display: flex;
            position: absolute;
            background: rgba(0,0,0,0.7);
            z-index: 100;
            width: 100%;
            height: 100%;
            border: 2px dashed rgb(103 232 249);
            animation: uiDisabledAni 1s infinite alternate;
            border-radius: 5px;
        }
        .ui-disabled::after {
            content: "Processing... hold your waifus.";
            text-decoration: italic;
            color: rgb(103 232 249);
            font-size: 1.5rem;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 15px;
            position: absolute;
            z-index: 100;
            width: 100%;
            height: 100%;
        }
        @keyframes uiDisabledAni {
            0% {
                opacity: 0.5;
            }
            100% {
                opacity: 1.0;
            }
        }
        """
