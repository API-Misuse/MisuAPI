package apr.myapr.parser.main;

import org.junit.Test;

import com.github.gumtreediff.client.Run;
import com.github.gumtreediff.gen.TreeGenerators;
import com.github.gumtreediff.tree.Tree;
import com.github.gumtreediff.tree.TreeContext;
import com.github.gumtreediff.utils.DaleFileUtil;

import apr.myapr.parser.main.Main;
import apr.myapr.parser.utils.FileUtil;

import static org.junit.Assert.*;

import java.io.IOException;

public class GumtreeTest {
    @Test
    public void testPythonParse() {
        Run.initGenerators();
        String srcFile = MainTest.getAbsFilePath("pythonFiles/nn_blocks.py");
        String saveFile = MainTest.getAbsFilePath("pythonFiles/nn_blocks.py.parser");
        try {
            DaleFileUtil.dstFileString = FileUtil.readFileToStr(srcFile);
            TreeContext src = TreeGenerators.getInstance().getTree(srcFile, null);
            Tree root = src.getRoot();
            FileUtil.writeToFile(saveFile, root.toTreeString(), false);
        } catch (UnsupportedOperationException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
