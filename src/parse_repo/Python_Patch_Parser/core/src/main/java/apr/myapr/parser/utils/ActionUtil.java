package apr.myapr.parser.utils;

import java.util.List;
import java.util.Map;

import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.actions.model.Addition;
import com.github.gumtreediff.actions.model.Delete;
import com.github.gumtreediff.actions.model.TreeAddition;
import com.github.gumtreediff.actions.model.TreeDelete;
import com.github.gumtreediff.actions.model.Update;
import com.github.gumtreediff.tree.Tree;
import com.github.gumtreediff.tree.TreeUtils;

public class ActionUtil {
    
    public static Map<String, String> actionStrMap = Map.of(
            "move-tree", "MOV",
            "insert-node", "INS",
            "insert-tree", "INS",
            "update-node", "UPD",
            "delete-tree", "DEL",
            "delete-node", "DEL"
            );
    
    public static Map<String, String> actionStrMap2 = Map.of(
            "move-tree", "TO",
            "insert-node", "TO",
            "insert-tree", "TO",
            "update-node", "TO",
            "delete-tree", "FROM",
            "delete-node", "FROM"
            );
    
    //TODO long text > 100
    public static String reformatString(Action ac) {
        String str = "";
        
        if (ac instanceof Addition) {
            Addition ad = (Addition) ac;
            Tree srcNode = ad.getNode();
            Tree dstNode = ad.getParent();
            
            str = getActionStr(ac, srcNode, dstNode);
            
            if(ActionUtil.has_api_call(srcNode) || ActionUtil.has_api_call(dstNode)) {
                ConfigUtil.api_call.add(str);
            }
            
            if(ActionUtil.is_stmt(srcNode)) {
                if(ActionUtil.has_api_call(srcNode)) {
                    ConfigUtil.api_call.add(str);
                }
            }else {
                if(ActionUtil.has_api_call(srcNode) || ActionUtil.has_api_call(srcNode)) {
                    ConfigUtil.api_call.add(str);
                }
            }
            
        }else if (ac instanceof TreeAddition) {
            TreeAddition ad = (TreeAddition) ac;
            
            str = getActionStr(ac, ad.getNode(), ad.getParent());
            
            if(ActionUtil.is_stmt(ad.getNode())) {
                if(ActionUtil.has_api_call(ad.getNode())) {
                    ConfigUtil.api_call.add(str);
                }
            }else {
                if(ActionUtil.has_api_call(ad.getNode()) || ActionUtil.has_api_call(ad.getParent())) {
                    ConfigUtil.api_call.add(str);
                }
            }
            
//            str = String.format("%s @type:%s@ %s @TO@ @type:%s@ %s",
//                    actionStrMap.get(ac.getName()),
//                    ad.getNode().getType().name, ad.getNode().getLabel(), 
//                    ad.getParent().getType().name, ad.getParent().getLabel()
//                    ); 
        }else if (ac instanceof Delete) {
            Delete del = (Delete) ac;
            
            str = getActionStr(ac, del.getNode(), del.getNode().getParent());
//            str = String.format("DEL @type:%s@ %s @FROM@ @type:%s@ %s",
//                    del.getNode().getType().name, del.getNode().getLabel(),
//                    del.getNode().getParent().getType().name, del.getNode().getParent().getLabel()
//                    );
            
            if(ActionUtil.is_stmt(del.getNode())) {
                if(ActionUtil.has_api_call(del.getNode())) {
                    ConfigUtil.api_call.add(str);
                }
            }else {
                if(ActionUtil.has_api_call(del.getNode()) || ActionUtil.has_api_call(del.getNode().getParent())) {
                    ConfigUtil.api_call.add(str);
                }
            }
        }else if (ac instanceof TreeDelete) {
            TreeDelete del = (TreeDelete) ac;
            
            str = getActionStr(ac, del.getNode(), del.getNode().getParent());
            
            if(ActionUtil.is_stmt(del.getNode())) {
                if(ActionUtil.has_api_call(del.getNode())) {
                    ConfigUtil.api_call.add(str);
                }
            }else {
                if(ActionUtil.has_api_call(del.getNode()) || ActionUtil.has_api_call(del.getNode().getParent())) {
                    ConfigUtil.api_call.add(str);
                }
            }
            
            
        }else if (ac instanceof Update) {
            Update up = (Update) ac;
            Tree srcNode = up.getNode();
            Tree dstNode = up.getUpdNode();
            
            str = getActionStr(ac, srcNode, dstNode);
            
//            str = String.format("UPlD @type:%s@ %s @TO@ @type:%s@ %s",
//                    up.getNode().getType().name, up.getNode().getLabel(), 
////                    "no_type", ad.getValue() // old version of gumtree
//                    up.getUpdNode().getType().name, up.getUpdNode().getLabel() // change version of gumtree
//                    ); 
            if(str.contains(" @type:atom_expr@ ")) {
                ConfigUtil.api_call.add(str);
            }
        }else {
            GeneralUtil.raiseException("unknown action: %s", ac.toString());
        }
        
        return str;
    }

    private static boolean is_stmt(Tree node) {
        String type = node.getType().name;
        if(type.contains("_stmt")){
            return true;
        }
        return false;
    }

    private static boolean has_api_call(Tree node) {
        List<Tree> child_nodes = TreeUtils.breadthFirst(node);
        
        for(Tree child : child_nodes) {
            if (child.getType().name.equals("atom_expr")) {
                return true;
            }
        }
        return false;
    }

    /**
     * use trim() to eliminate whitespaces and \n at the end of each line
     * @param ac
     * @param srcNode
     * @param dstNode
     * @return
     */
    private static String getActionStr(Action ac, Tree srcNode, Tree dstNode) {
        String str = String.format("%s @type:%s@ @[%s,%s]@ %s @%s@ @type:%s@ @[%s,%s]@ %s",
                actionStrMap.get(ac.getName()),
                srcNode.getType().name, srcNode.getPos(), srcNode.getEndPos(), ActionUtil.short_str(srcNode), 
                actionStrMap2.get(ac.getName()), // from || to
                dstNode.getType().name, dstNode.getPos(), dstNode.getEndPos(), ActionUtil.short_str(dstNode)
                ); 
        return str;
    }

    private static Object short_str(Tree ast_node) {
        String ast_str = ast_node.getLabel().trim();
        int max_len = 50;
        if (ast_str.length() > max_len){
            ast_str = String.format("%s <text_longer_than_%s>", ast_str.substring(0, max_len), max_len);
        }
        return ast_str;
    }
}
