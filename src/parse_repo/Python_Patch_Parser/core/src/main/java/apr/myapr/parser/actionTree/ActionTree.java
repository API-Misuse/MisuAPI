package apr.myapr.parser.actionTree;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.actions.model.Addition;
import com.github.gumtreediff.actions.model.Delete;
import com.github.gumtreediff.actions.model.TreeAddition;
import com.github.gumtreediff.actions.model.TreeDelete;
import com.github.gumtreediff.actions.model.Update;
import com.github.gumtreediff.tree.Tree;

import apr.myapr.parser.utils.ActionUtil;
import apr.myapr.parser.utils.GeneralUtil;

/**
 * this is to regroup the actions into a tree structure.
 * 
 * this class learns from com.github.gumtreediff.tree.AbstractTree & DefaultTree (Gumtree 3.0.0-beta1)
 * 
 * @author apr
 *
 */
public class ActionTree {
    private Action action;
    private List<ActionTree> children = new ArrayList<>();
    private ActionTree parent;
    
    public ActionTree(Action action) {
        setAction(action);
    }

    public boolean isLeaf() {
        return children.isEmpty();
    }
    
    public boolean isRoot() {
        return parent == null;
    }
    
    public ActionTree getRoot() {
        ActionTree root = this;
        while (root.getParent() != null) {
            root = root.getParent();
        }
        return root;
    }
    
    public List<ActionTree> getChildren() {
        return children;
    }

    public void setChildren(List<ActionTree> children) {
        Iterator<ActionTree> iter = children.iterator();
        
        while(iter.hasNext()) {
            ActionTree tree = iter.next();
            tree.setParent(this);
        }
    }
    
    public void addChild(ActionTree tree) {
        this.children.add(tree);
        tree.setParent(this);
    }

    public ActionTree getParent() {
        return parent;
    }

    public void setParent(ActionTree parent) {
        this.parent = parent;
    }

    public Action getAction() {
        return action;
    }

    public void setAction(Action action) {
        this.action = action;
    }

    /**
     * hierarchical tree print
     * @param n: default start from 1 (means that children need to add prefix "---" once.
     * @return
     */
    public String toHierarchicalString(int n) {
        String hierStr = String.format("%s\n", ActionUtil.reformatString(action).trim());
        for (ActionTree at : children) {
            String preStr = "";
            for(int i = 0; i < n; i ++) {
                preStr += "---";
            }
            hierStr += String.format("%s%s\n", preStr, at.toHierarchicalString(n + 1).trim());
        }
        
        return hierStr;
    }

    @Override
    public String toString() {
        return action.toString();
    }


}
