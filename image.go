package main

import (
	"bufio"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
)

func downloadImage(urlStr string, filepath string) error {
	resp, err := http.Get(urlStr)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	return err
}

func downloadImagesFromTxtFile(txtFilePath string, saveDir string) error {
	file, err := os.Open(txtFilePath)
	if err != nil {
		return err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	lineCount := 0
	for scanner.Scan() {
		lineCount++
	}
	file.Seek(0, 0)

	filenameFormat := fmt.Sprintf("%%0%dd.%%s", len(strconv.Itoa(lineCount)))

	scanner = bufio.NewScanner(file)
	lineNumber := 1
	for scanner.Scan() {
		urlStr := scanner.Text()
		parsedURL, err := url.Parse(urlStr)
		if err != nil {
			return err
		}
		queryParams := parsedURL.Query()
		extension := queryParams.Get("format")
		if extension == "" {
			extension = "jpg"  // デフォルトの拡張子を設定
		}
		filename := fmt.Sprintf(filenameFormat, lineNumber, extension)
		filepath := filepath.Join(saveDir, filename)

		err = downloadImage(urlStr, filepath)
		if err != nil {
			return err
		}

		// ファイル名をダウンロードしたことを表示
		fmt.Println("Downloaded:", filename)

		lineNumber++
	}

	if err := scanner.Err(); err != nil {
		return err
	}

	return nil
}

func main() {
	txtFilePath := "image_urls.txt"
	saveDir := "./imggo"

	if _, err := os.Stat(saveDir); os.IsNotExist(err) {
		os.Mkdir(saveDir, 0755)
	}

	err := downloadImagesFromTxtFile(txtFilePath, saveDir)
	if err != nil {
		fmt.Println("Error:", err)
	}
}