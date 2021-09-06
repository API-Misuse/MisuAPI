package apr.myapr.parser.utils;

import java.io.BufferedInputStream;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class FileUtil {
	/**
	 * method from tbar
	 * @param file
	 * @return
	 */
	public static String readFileToStr1(File file) {
		byte[] input = null;
		BufferedInputStream bis = null;
		
		try {
			bis = new BufferedInputStream(new FileInputStream(file));
			input = new byte[bis.available()];
			bis.read(input);
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			close(bis);
		}
		
		String sourceCode = null;
		if (input != null) {
			sourceCode = new String(input);
		}
		
		return sourceCode;
	}
	
	private static void close(BufferedInputStream bis) {
		try {
			if (bis != null) {
				bis.close();
				bis = null;
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	/**
	 * my method to read file into string
	 */
	public static String readFileToStr(String filePath) {
		String str = null;
		try {
			str = Files.readString(Path.of(filePath));
		} catch (IOException e) {
			e.printStackTrace();
		}
		return str;
	}
	

	// default: logPath
//	public static void writeToFile(String content){
//		writeToFile(FileUtil.logPath, content, true);
//	}

	public static void writeToFile(String path, String content){
		writeToFile(path, content, true);
	}

	public static void writeToFile(String path, String content, boolean append){
		// logger.info(content);
		// get dir
		if (path.contains("/")){
			String dirPath = path.substring(0, path.lastIndexOf("/"));
			File dir = new File(dirPath);
			if (!dir.exists()){
				dir.mkdirs();
				System.out.println(String.format("%s does not exists, and are created now via mkdirs()", dirPath));
			}
		}

		BufferedWriter output = null;
		try {
			output = new BufferedWriter(new FileWriter(path, append));
			output.write(content);
			// output.close();
		} catch (final IOException e) {
			e.printStackTrace();
		}finally {
			try {
				output.close();
			} catch (IOException ex) {
				// Log error writing file and bail out.
				ex.printStackTrace();
			}
		}
	}

}
