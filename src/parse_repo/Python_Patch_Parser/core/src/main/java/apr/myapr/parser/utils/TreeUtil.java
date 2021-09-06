package apr.myapr.parser.utils;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.actions.model.Addition;
import com.github.gumtreediff.actions.model.Delete;
import com.github.gumtreediff.actions.model.Insert;
import com.github.gumtreediff.actions.model.Move;
import com.github.gumtreediff.actions.model.TreeAddition;
import com.github.gumtreediff.actions.model.TreeDelete;
import com.github.gumtreediff.actions.model.TreeInsert;
import com.github.gumtreediff.actions.model.Update;
import com.github.gumtreediff.tree.Tree;
import com.github.gumtreediff.tree.Type;

import apr.myapr.parser.actionTree.ActionTree;

public class TreeUtil {
    private static final String LONG_TEXT = "long_text_longer_than_100";;

    public static void actionsToTree(List<Action> actions) {
        FileUtil.writeToFile(ConfigUtil.outputPath, "", false);
        
        List<ActionTree> atList = new ArrayList<>();
        for (Action ac : actions) {
            // abandon actions larger than statements.
            if (isLargerThanStmt(ac.getNode())) {
                continue;
            }
            
            atList.add(new ActionTree(ac));
        }
        
        for(int i = 0; i < atList.size(); i ++) {
            ActionTree at = atList.get(i);
            Tree srcNode = at.getAction().getNode();
            for (int j = i + 1; j < atList.size(); j ++) {
                ActionTree atOther = atList.get(j);
                Tree srcNodeOther = atOther.getAction().getNode();
                
                // insert should be considered exclusively
                if (getParentNode(at, srcNode).equals(srcNodeOther)) {
                    atOther.setParent(at);
                }
                if(getParentNode(atOther, srcNodeOther).equals(srcNode)) {
                    at.addChild(atOther);
                }
            }
        }
        
        List<ActionTree> rootTrees = new ArrayList<>();
        for (ActionTree at : atList) {
            ActionTree root = at.getRoot();
            
            if (!rootTrees.contains(root)) {
                rootTrees.add(root);
            }
        }
        
        for (ActionTree rt : rootTrees) {
            String represent = rt.toHierarchicalString(1);
            System.out.format("\nActionSet:\n%s", represent);
            FileUtil.writeToFile(ConfigUtil.outputPath, represent + "\n\n");
        }
    }

    private static Tree getParentNode(ActionTree at, Tree srcNode) {
        Action ac = at.getAction();
        if (ac instanceof Insert) {
            return ((Insert) ac).getParent();
        } else if (ac instanceof TreeInsert) {
            return ((TreeInsert) ac).getParent();
        } else {
            return srcNode.getParent();
        }
    }

    /**
     * all types of python AST nodes can be found at: https://docs.python.org/3/reference/grammar.html
     * @param node
     * @return
     */
    private static boolean isLargerThanStmt(Tree node) {
        Tree parent = node;
        while(parent != null) {
            String type = parent.getType().name;
            if (type.endsWith("_stmt")) {
                return false;
            }
            parent = parent.getParent();
        }
        return true;
    }
    
//    public static Map<String, String> actionStrMap = Map.of(
//            "move-tree", "MOV",
//            "insert-node", "INS",
//            "insert-tree", "INS",
//            "update-node", "UPD",
//            "delete-tree", "DEL",
//            "delete-node", "DEL"
//            );
//    
//    public static void printNodeInfo(String srcFileString, String dstFileString, Tree node) {
//        int startPos = node.getPos();
//        int endPos = node.getEndPos();
//        
//        System.out.format("\n\nNode Info: \ntoString: %s \nlabel: %s \ntype: %s \nstring: %s ~~ %s\n", 
//                node.toTreeString(), 
//                node.getLabel(),
//                node.getType(),
//                srcFileString.substring(startPos, endPos),
//                dstFileString.substring(startPos, endPos)
//                );
//    }
//
//    public static Tree getFileInput(Tree node) {
//        while(!node.getType().name.equals("file_input")) {
//            node = node.getParent();
//        }
//        return node;
//    }
//    
//    public static void printAction(Action action, String srcFileString, String dstFileString) {
//        //
////      Tree file_input = getFileInput(action.getNode());
////      String path = "/mnt/2020-11-API-misuse/Repair_API_Misuse/api-misuse-repair/1_collect_dl_applications/Python_Patch_Parser/core/src/test/resources/diffFiles/1.py.parser";
////      MyFileUtil.writeToFile(path, file_input.toTreeString());
//        
//        
//        Tree srcNode = action.getNode();
//        Tree dstIns = null;
//        
//        int srcStartPos = srcNode.getPos();
//        int srcEndPos = srcNode.getEndPos();
//        int dstStartPos;
//        int dstEndPos;
//        
//        // insert-tree, move-tree
//        if (action instanceof TreeAddition) {
//            dstIns = ((TreeAddition) action).getParent(); 
//            printForAddtion(action, srcNode, dstIns, srcFileString, dstFileString);
//        }
//        // insert-node
//        if (action instanceof Addition) {
//            dstIns = ((Addition) action).getParent(); 
//            printForAddtion(action, srcNode, dstIns, srcFileString, dstFileString);
//        }
//        
//        // update-node
//        if (action instanceof Update) {
//            String srcStr = srcFileString.substring(srcStartPos, srcEndPos);
//            String dstValue = ((Update) action).getValue(); 
//            // replace ori by new
//            System.out.format("%s %s@@[%s,%s]@@ \"%s\" @TO@ %s@@[%s,%s]@@ \"%s\" \n",
//                    actionStrMap.get(action.getName()),
//                    srcNode.getType(), srcStartPos, srcEndPos,
//                    srcStr,
//                    // @TO@
//                    srcNode.getType(), srcStartPos, srcStartPos + dstValue.length(), 
//                    dstValue);
//            // not available to localize new value by substring.
////          logger.debug("value str: {}" , dstFileString.substring(srcStartPos, srcStartPos + dstValue.length()));
//            
//            Tree parent = srcNode;
//            Type type = parent.getType();
//            while (parent != null && !type.name.endsWith("_stmt") && !type.name.equals("file_input")) {
//                parent = parent.getParent();
//                type = parent.getType();
//                
//                printParentUpdate(action, parent, srcFileString, dstValue, srcStartPos, srcEndPos);
//            }
//        }
//        
//        // delete-node, delete-tree
//        if (action instanceof Delete || action instanceof TreeDelete) {
//            printForDelete(action, srcNode, srcFileString);
//            
//            // loop
////          Tree parent = srcNode;
////          Type type = parent.getType();
////          while (parent != null && !type.name.endsWith("_stmt") && !type.name.equals("file_input")) {
////              parent = parent.getParent();
////              type = parent.getType();
////              
////              printParentDelete(action, parent, srcFileString, dstValue, srcStartPos, srcEndPos);
////          }
//        }
//    }
//    
//    private static void printForDelete(Action action, Tree srcNode, String srcFileString) {
//        int srcStartPos = srcNode.getPos();
//        int srcEndPos = srcNode.getEndPos();
//        
//        String srcStr = srcFileString.substring(srcStartPos, srcEndPos);
//        
//        Tree parent = srcNode.getParent();
//        String parentStr = srcFileString.substring(parent.getPos(), parent.getEndPos());
//        if (parentStr.length() > 100) {
//            parentStr = LONG_TEXT;
//        }
//        
//        System.out.format("%s %s@@[%s,%s]@@ \"%s\" @FROM@ %s@@[%s,%s]@@ \"%s\" \n",
//                actionStrMap.get(action.getName()),
//                srcNode.getType(), srcStartPos, srcEndPos,
//                srcStr,
//                // @TO@
//                parent.getType(), parent.getPos(), parent.getEndPos(), 
//                parentStr);
//        
//    }
//
//    public static void printParentUpdate(Action action, Tree srcNode, String srcFileString, String dstValue,
//            int dstStartPos, int dstEndPos) {
//        int srcStartPos = srcNode.getPos();
//        int srcEndPos = srcNode.getEndPos();
//        String srcStr = srcFileString.substring(srcStartPos, srcEndPos);
//        
//        // this is a good apprach to get the dstStr via pos calculation
//        String dstStr = srcFileString.substring(srcStartPos, dstStartPos) + dstValue + srcFileString.substring(dstEndPos, srcEndPos);
//        
//        System.out.format("%s %s@@[%s,%s]@@ \"%s\" @TO@ %s@@[%s,%s]@@ \"%s\" \n",
//                actionStrMap.get(action.getName()),
//                srcNode.getType(), srcStartPos, srcEndPos,
//                srcStr,
//                // @TO@
//                srcNode.getType(), srcStartPos, srcStartPos + dstStr.length(), 
//                dstStr);
//    }
//    
//    /**
//     * print for addition and treeAddition
//     * @param srcNode
//     * @param dstIns
//     * @param srcFileString
//     * @param dstInsStr
//     */
//    public static void printForAddtion(Action action, Tree srcNode, Tree dstIns, String srcFileString, String dstFileString) {
//        int srcStartPos = srcNode.getPos();
//        int srcEndPos = srcNode.getEndPos();
//        
//        int dstStartPos = dstIns.getPos();
//        int dstEndPos = dstIns.getEndPos();
//        
//        String srcStr = dstFileString.substring(srcStartPos, srcEndPos);
//        
//        String dstInsStr = "";
//        if (dstIns.getLength() < 100) {
//            dstInsStr = srcFileString.substring(dstStartPos, dstEndPos);
//        }else {
//            dstInsStr = LONG_TEXT;
//        }
//        
//        // move-tree: move original to ori. So both the srcNode and dstIns belong to the original file
//        if (action.getName().equals("move-tree")) {
//            srcStr = srcFileString.substring(srcStartPos, srcEndPos);
//            
//            // faulty code does work
////              dstInsStr = dstFileString.substring(dstStartPos, dstEndPos);
////              dstInsStr = srcFileString.substring(dstStartPos, dstEndPos);
//            
//            int dstMovPos = ((Move) action).getPosition(); // + 1 to localize the moved node. NO. I cannot localize the moved node, as the dstIns node is in original file.
//            Tree dstMovNode = dstIns.getChild(dstMovPos); // get the moved ast node
//            dstStartPos = dstMovNode.getPos();
//            dstEndPos = dstMovNode.getEndPos();
//            dstInsStr = srcFileString.substring(dstStartPos, dstEndPos);
////          logger.debug("dstInsStr: {}" , dstInsStr);
//            
//            System.out.format("%s %s@@[%s,%s]@@ \"%s\" @AFTER@ %s@@[%s,%s]@@ \"%s\" \n",
//                    actionStrMap.get(action.getName()),
//                    srcNode.getType(), srcStartPos, srcEndPos,
//                    srcStr,
//                    // @TO@
//                    //print the moved ast node. but maintain its' parent type
//                    // not maintain now
//                    dstMovNode.getType(), dstStartPos, dstEndPos, 
//                    dstInsStr);
//            
//        }else {
//            System.out.format("%s %s@@[%s,%s]@@ \"%s\" @TO@ %s@@[%s,%s]@@ \"%s\" \n",
//                    actionStrMap.get(action.getName()),
//                    srcNode.getType(), srcStartPos, srcEndPos,
//                    srcStr,
//                    // @TO@
//                    dstIns.getType(), dstStartPos, dstEndPos, 
//                    dstInsStr);
//        }
//    }
}
