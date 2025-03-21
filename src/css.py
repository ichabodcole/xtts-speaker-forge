def app_css():
    common_css = """
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

    import_css = """
        .import-speaker-to-list {
            padding: 0px 10px 10px;
            max-height: 600px;
            overflow-y: auto;
        }
        
        /* Style the current speakers list to match the grid layout */
        .import-speaker-to-list ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 8px;
        }
        
        .import-speaker-to-list li {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            padding: 8px;
            margin: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    """

    changelog_css = """
        .changelog-content {
            padding: 0 10px 15px;
            font-size: 1.1em;
        }
    """

    about_css = """
        .about-content {
            padding: 0 10px 15px;
            font-size: 1.1em;
        }
    """
    
    # Add the grid layout CSS for speaker checkboxes
    speaker_grid_css = """
        /* Grid layout for speaker checkboxes */
        .speaker-checkbox-grid .wrap {
            display: grid !important;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 8px;
        }

        .speaker-checkbox-grid .wrap label {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            padding: 8px;
            margin: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            transition: background-color 0.2s ease;
        }

        .speaker-checkbox-grid .wrap label:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        /* Ensure consistent checkbox size */
        .speaker-checkbox-grid .wrap input[type="checkbox"] {
            width: 16px;
            height: 16px;
            margin-right: 8px;
        }
    """

    return f"{common_css}\n{import_css}\n{changelog_css}\n{about_css}\n{speaker_grid_css}"
