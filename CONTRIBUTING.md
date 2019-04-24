# Contributing to eve-trajectory-mining

The following is a set of guidelines for contributing to the research project. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[What should I know before I get started?](#what-should-i-know-before-i-get-started)
  * [Handling Large CSV Files](#handling-large-csv-files)
    * [Issues](#issues)
  * [Killmail Fetching](#killmail-fetching)
    * [/killmail_scrapes](#killmail-scrapes)
  * [Trajectory Mining](#trajectory-mining)
    * [/data](#data)

## Code of Conduct

Please use pull requests for all changes and document everything you do. This includes in-line notes in your code as well as commit descriptions!

## What should I know before I get started?

### Handling Large CSV Files

This project features about 9Gb of raw data and around 2Gb of filtered data. As such, we chosen to host the data using **Git Large File Storage (Git-LFS)** <https://help.github.com/en/articles/versioning-large-files>. Installing this plugin is necessary to download/access the `.csv` files. To get started...

1) Visit <https://git-lfs.github.com/> to install the plugin.
2) Run these commands in your terminal rooted at the repository:
  - `git lfs install`
  - `git track "*.csv"`
3) Make sure you see `.gitattributes` in the root directory. If it's not there, run
  - `git add .gitattributes`

After performing those steps, you'll be able to fetch/merge/pull/commit/etc. all of the `.csv` files in the repository!

#### Issues

If you have issues using **Git Large File Storage (Git-LFS)**, here are some resouces to guide troubleshooting:
- Home Page: <https://help.github.com/en/articles/versioning-large-files>
- Installation: <https://help.github.com/en/articles/configuring-git-large-file-storage>
- Upload Failure: <https://help.github.com/en/articles/resolving-git-large-file-storage-upload-failures>
- Storing Existing CSV Files: <https://help.github.com/en/articles/moving-a-file-in-your-repository-to-git-large-file-storage>
- Collaboration using Git-LFS: <https://help.github.com/en/articles/collaboration-with-git-large-file-storage>

### Killmail Fetching

This application is used ***exclusively*** for scraping raw data for the project. See README for usage guidelines.

- If you modify the raw data in any way, the resulting data sets should be stored in the [Trajectory Mining](#trajectory-mining) directory.

#### /killmail_scrapes

This folder contains the raw data scraped using the [Killmail Fetching](#killmail-fetching) application. Please see [Handling Large CSV Files](#handling-large-csv-files) for help with installing the plugins necessary to view the files in this directory.

### Trajectory Mining

This application is used ***exclusively*** for filtering/analyzing/visualizing raw data sets from the [Killmail Fetching](#killmail-fetching) application. See README for usage guidelines.

- If you need to collect more raw data or modify the filtered data using the raw data already obtained, obtain/store the raw data in the [Killmail Fetching](#killmail-fetching) application.


#### /data

This folder contains filtered data used in the trajectory mining process. Please see [Handling Large CSV Files](#handling-large-csv-files) for help with installing the plugins necessary to view the files in this directory.
