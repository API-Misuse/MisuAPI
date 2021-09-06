package apr.myapr.parser.utils;

public class GeneralUtil {
    /**
     * @Description
     * raise an exception when necessary 
     * @author apr
     * @version Oct 4, 2020
     *
     * @param expInfo
     */
    public static void raiseException(String expInfo) {
        try {
            throw new Exception(String.format("===raiseException: %s", expInfo));
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        System.exit(0);
    }
    
    /**
     * @Description
     * string with format 
     * @author apr
     * @version Oct 12, 2020
     *
     * @param format
     * @param args
     */
    public static void raiseException(String format, Object... args){
        try {
            throw new Exception(String.format(format, args));
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        System.exit(0);
    }
}
