package apr.myapr.parser.utils;

import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class ConfigUtil {
	final static Logger logger = LoggerFactory.getLogger(ConfigUtil.class);

	public static String srcFilePath;
	public static String dstFilePath;

    public static String outputPath;	
    
    public static List<String> api_call = new ArrayList<>();
}
