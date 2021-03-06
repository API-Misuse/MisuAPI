/*
 * This Java source file was generated by the Gradle 'init' task.
 */
package apr.myapr.parser.main;

import org.junit.Test;

import apr.myapr.parser.main.Main;

import static org.junit.Assert.*;

import java.io.File;

public class MainTest {
    @Test public void testSomeLibraryMethod() {
        Main classUnderTest = new Main();
        assertTrue("someLibraryMethod should return 'true'", classUnderTest.someLibraryMethod());
    }
    
    @Test 
    public void testMain1() {
    	String srcPath = getAbsFilePath("diffFiles/repo_download_and_parse.py");
    	String dstPath = getAbsFilePath("diffFiles/repo_download_and_parse-2.py");
    			
    	String input = String.format("-srcFilePath %s -dstFilePath %s", 
    			srcPath,
    			dstPath);
    	String[] args = input.split(" ");
    	Main.main(args);
    }
    
    @Test 
    public void testMain2() {
    	String srcPath = getAbsFilePath("diffFiles/collect_repos.py");
    	String dstPath = getAbsFilePath("diffFiles/collect_repos-2.py");
    			
    	String input = String.format("-srcFilePath %s -dstFilePath %s", 
    			srcPath,
    			dstPath);
    	String[] args = input.split(" ");
    	Main.main(args);
    }
    
    @Test 
    public void testMain3() {
    	String srcPath = getAbsFilePath("diffFiles/1.py");
    	String dstPath = getAbsFilePath("diffFiles/2.py");
    			
    	String input = String.format("-srcFilePath %s -dstFilePath %s", 
    			srcPath,
    			dstPath);
    	String[] args = input.split(" ");
    	Main.main(args);
    }
    
    @Test 
    public void testMainForJavaDiff1() {
//    	String srcPath = "/home/apr/apr_tools/GumTree_repos/gumtree/benchmark/defects4j/Math_11/MultivariateNormalDistribution/Math_11_MultivariateNormalDistribution_s.java";
//    	String dstPath = "/home/apr/apr_tools/GumTree_repos/gumtree/benchmark/defects4j/Math_11/MultivariateNormalDistribution/Math_11_MultivariateNormalDistribution_t.java";
    	
    	String srcPath = getAbsFilePath("diffFiles/java/simple_math11_1.java");
    	String dstPath = getAbsFilePath("diffFiles/java/simple_math11_1.java");
    			
    	String input = String.format("-srcFilePath %s -dstFilePath %s", 
    			srcPath,
    			dstPath);
    	String[] args = input.split(" ");
    	Main.main(args);
    }
    
    public static String getAbsFilePath(String path) {
    	File fileDirectory = new File("src/test/resources");
    	String absFilePath = fileDirectory.getAbsoluteFile() + "/" + path;
    	return absFilePath;
    }
}
