/*
 * This Java source file was generated by the Gradle 'init' task.
 */
package apr.myapr.parser.main;

import com.github.gumtreediff.actions.Diff;
import com.github.gumtreediff.actions.EditScript;
import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.client.Run;
import com.github.gumtreediff.matchers.GumTreeProperties;
import com.github.gumtreediff.tree.Tree;
import com.github.gumtreediff.tree.Type;

import apr.myapr.parser.utils.ConfigUtil;
import apr.myapr.parser.utils.FileUtil;
import apr.myapr.parser.utils.TreeUtil;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Main {
	
	final static Logger logger = LoggerFactory.getLogger(Main.class);
	
	public static void main(String[] args) {
		setParameters(args);
		
		getDiff();
	}
	
	private static void setParameters(String[] args) {
		Option opt1 = new Option("sfp","srcFilePath",true,"e.g., /home/apr/apr_tools/GumTree_repos/gumtree/my_test/repo_download_and_parse.py");
        opt1.setRequired(true);
        Option opt2 = new Option("dfp","dstFilePath",true,"e.g., /home/apr/apr_tools/GumTree_repos/gumtree/my_test/repo_download_and_parse-2.py");
        opt2.setRequired(true);
        
        Option opt3 = new Option("op","outputPath",true,"e.g., /home/apr/apr_tools/GumTree_repos/gumtree/my_test/output.txt");
        opt3.setRequired(false);
        
        Options options = new Options();
        options.addOption(opt1);
        options.addOption(opt2);
        options.addOption(opt3);
        
        CommandLine cli = null;
        CommandLineParser cliParser = new DefaultParser();
        HelpFormatter helpFormatter = new HelpFormatter();

        try {
            cli = cliParser.parse(options, args);
        } catch (org.apache.commons.cli.ParseException e) {
            helpFormatter.printHelp(">>>>>> test cli options", options);
            e.printStackTrace();
        } 

        if (cli.hasOption("srcFilePath")){
        	ConfigUtil.srcFilePath = cli.getOptionValue("srcFilePath");
        }
        if(cli.hasOption("dstFilePath")){
            ConfigUtil.dstFilePath = cli.getOptionValue("dfp");
        }
        if(cli.hasOption("op")) {
            ConfigUtil.outputPath = cli.getOptionValue("op");
        }
	}

	public static void getDiff() {
		//Diff.compute(MyUtil.srcFilePath, MyUtil.srcFilePath, opts.treeGeneratorId, opts.matcherId, opts.properties);
		Run.initGenerators();
		GumTreeProperties properties = new GumTreeProperties();
		try {
			/*
			 * gumtree-complete  many
			 * gumtree-simple proper
			 * gumtree  many
			 * xy    many*2
			 * change-distiller  many*3
			 * gumtree-simple-id  same to gumtree-simple
			 * theta    same to gumtree-complete
			 * rted-theta
			 * longestCommonSequence
			 * classic-gumtree-theta  good now.
			 * gumtree-simple-id-theta
			 * 
			 * 
			 * winner: gumtree-simple-id-theta
			 */
			Diff diff = Diff.compute(ConfigUtil.srcFilePath, ConfigUtil.dstFilePath, null, "gumtree-simple-id-theta", properties);
			EditScript editScript = diff.editScript;
			List<Action> actions = editScript.asList();
			
//			String srcFileString = MyFileUtil.readFileToStr1(new File(MyUtil.srcFilePath));
//			String dstFileString = MyFileUtil.readFileToStr1(new File(MyUtil.dstFilePath));
			String srcFileString = FileUtil.readFileToStr(ConfigUtil.srcFilePath);
			String dstFileString = FileUtil.readFileToStr(ConfigUtil.dstFilePath);
			// compare two methods
//			compareReadFileToStr();
			logger.info("srcFileString len: {}", srcFileString.length());
			logger.info("dstFileString len: {}", dstFileString.length());
			
			
			System.out.format("The patch diff is as follows:\n\n");
			for (int i = 0; i < actions.size(); i ++) {
				Action action = actions.get(i);
				System.out.format("\n\nAction %s:\n", i + 1);
				System.out.println(action.toString() + "\n\n");
//				MyUtil.printAction(action,srcFileString,dstFileString);
			}
			
			TreeUtil.actionsToTree(actions);
			
			// write api_calls
			String api_str = "";
			for(String str : ConfigUtil.api_call) {
			    api_str += str + "\n\n";
			}
			FileUtil.writeToFile(ConfigUtil.outputPath+".api", api_str, false);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
    private static void compareReadFileToStr() {
    	String srcFileString = FileUtil.readFileToStr1(new File(ConfigUtil.srcFilePath));
		String dstFileString = FileUtil.readFileToStr1(new File(ConfigUtil.dstFilePath));
		
		String srcFileString2 = FileUtil.readFileToStr(ConfigUtil.srcFilePath);
		String dstFileString2 = FileUtil.readFileToStr(ConfigUtil.dstFilePath);
		
		assert srcFileString.equals(srcFileString2) : "srcFileString does not equal srcFileString2";
		assert dstFileString.equals(dstFileString2) : "dstFileString does not equal dstFileString2";
		
		logger.info("srcFileString len: {}", srcFileString.length());
		logger.info("dstFileString len: {}", dstFileString.length());
		
		logger.info("srcFileString2 len: {}", srcFileString2.length());
		logger.info("dstFileString2 len: {}", dstFileString2.length());
	}

	public boolean someLibraryMethod() {
        return true;
    }
}
