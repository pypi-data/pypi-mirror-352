# 📚 FanFic Downloader CLI Guide

> *Your ultimate companion for downloading and managing fan fiction stories from across the web!*

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Introduction

FanFic Downloader CLI is a powerful command-line tool that helps you download, organize, and manage fan fiction stories from various websites. Powered by FanFicFare under the hood, it provides a beautiful, user-friendly interface to interact with your favorite stories.

![Demo Screenshot](https://via.placeholder.com/800x400)

## ⚡ Features

- 📥 **Easy Downloads**: Download stories with a simple command
- 📋 **Batch Processing**: Handle multiple stories at once
- 🔍 **URL Extraction**: Extract story URLs from author profiles and series pages
- 📁 **Library Management**: Keep track of your downloaded stories
- 🎨 **Beautiful Interface**: Rich text formatting for an enhanced experience
- ⚙️ **Customizable Settings**: Configure download locations and preferences

## 📦 Installation

### Using pip (Recommended)

```bash
pip install fanfic-downloader
```

### From Source

```bash
git clone https://github.com/yourusername/fanfic-downloader.git
cd fanfic-downloader
pip install -e .
```

## 🚀 Getting Started

After installation, you can start using the `fanfic` command in your terminal:

```bash
fanfic --help
```

This will display all available commands and options.

## 📘 Basic Usage

### 💾 Downloading Stories

Download a story by providing its URL:

```bash
fanfic download -u https://archiveofourown.org/works/12345678
```

Download multiple stories at once:

```bash
fanfic download -u https://archiveofourown.org/works/12345678 https://archiveofourown.org/works/87654321
```

Download stories listed in a text file:

```bash
fanfic download -f my_stories.txt
```

### 🔎 Interactive Mode

If you don't have URLs ready, you can use the interactive mode:

```bash
fanfic download -i
```

This will prompt you to enter URLs one by one.

## 🔥 Advanced Features

### 📋 Extracting Story URLs

Extract story URLs from an author's profile or series page:

```bash
fanfic extract -u https://archiveofourown.org/users/authorname/works
```

Save extracted URLs to a file:

```bash
fanfic extract -u https://archiveofourown.org/series/12345 -o extracted_urls.txt
```

Extract and download in one command:

```bash
fanfic extract -u https://archiveofourown.org/users/authorname/works -d
```

### 📚 Managing Your Library

List all downloaded stories:

```bash
fanfic list
```

Get detailed information about your stories:

```bash
fanfic list -d
```

Sort stories by size, date, or name:

```bash
fanfic list -s size
```

### ⚙️ Configuring Settings

View current settings:

```bash
fanfic settings
```

Change the download folder:

```bash
fanfic settings -f /path/to/new/folder
```

Open the download folder:

```bash
fanfic settings -o
```

## 💡 Use Cases

### 📱 For Mobile Readers

1. Download your favorite stories using FanFic Downloader CLI
2. Transfer the EPUB files to your e-reader or mobile device
3. Enjoy reading on the go, even without internet access!

### 🏫 For Series Bingers

1. Find a series you love with multiple stories
2. Extract all story URLs with a single command:
   ```bash
   fanfic extract -u https://archiveofourown.org/series/12345 -d
   ```
3. All stories will be downloaded automatically for a binge-reading session!

### 🔍 For Archive Explorers

1. Discover a new author with a large collection
2. Extract all their stories with:
   ```bash
   fanfic extract -u https://archiveofourown.org/users/authorname/works -o author_stories.txt
   ```
3. Review the list and select favorites
4. Download selected stories:
   ```bash
   fanfic download -f author_stories.txt
   ```

### 🌙 For Offline Reading

1. Before a trip or when you know you'll be without internet:
2. Prepare a list of stories you want to read
3. Run a batch download:
   ```bash
   fanfic download -f vacation_reading.txt
   ```
4. All stories will be available offline in EPUB format!

## 🛠️ Tips & Tricks

### 💻 Command Aliases

Create aliases for commonly used commands:

```bash
# On Linux/macOS
alias fanfic-dl="fanfic download -i"
alias fanfic-list="fanfic list -d"

# On Windows (PowerShell)
function FanficDL { fanfic download -i }
function FanficList { fanfic list -d }
```

### 📅 Scheduled Downloads

Use cron jobs (Linux/macOS) or Task Scheduler (Windows) to automatically download new chapters from a list of URLs:

```bash
# Example cron job (Linux/macOS)
0 9 * * * /usr/local/bin/fanfic download -f ~/ongoing_stories.txt
```

### 🔄 Workflow Integration

Combine with other tools for an enhanced workflow:

1. Use `grep` or `find` to search through your downloaded stories
2. Convert EPUBs to other formats using Calibre
3. Set up a personal server to access your stories remotely

## 🚨 Troubleshooting

### ❓ Common Issues

**Issue**: Command not found after installation
**Solution**: Ensure your Python scripts directory is in your PATH

**Issue**: Download fails for certain stories
**Solution**: Check if the story requires login or age verification and use:

```bash
fanfic download -u URL -o "is_adult=true"
```

**Issue**: Extraction yields no results
**Solution**: Some sites may block automated tools. Try:

```bash
fanfic extract -u URL -o "delay_between_pages=3"
```

## 🤝 Contributing

Contributions are welcome! If you'd like to help improve FanFic Downloader CLI:

1. Fork the repository
2. Create a feature branch: `git checkout -b new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin new-feature`
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FanFicFare](https://github.com/JimmXinu/FanFicFare) for providing the core downloading functionality
- [Typer](https://typer.tiangolo.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/en/stable/introduction.html) for the beautiful terminal formatting

---

Made with ❤️ by Munish Chandra Jha

*Happy reading!* 📚✨
