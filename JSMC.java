//"%UserProfile%\Desktop\Apps\jdk-16\bin\javac.exe" JSMC.java
//"%UserProfile%\Desktop\Apps\jdk-16\bin\java.exe" JSMC
import java.util.Random;

class VoidFunc
{
    public int data;
    public VoidFunc() {}
    public void invoke() { data += 1; }
}

class IntFunc
{
    private Random r;
    public IntFunc(Random r) { this.r = r; }
    public int invoke() { return r.nextInt(3); }
}

abstract class IrredLoop
{
    final int EXIT = 0;
    final int LOOP = 1;
    final int FORWARD = 2;
    public abstract void invoke(boolean u_start,
    IntFunc w_cond, IntFunc x_cond,
    VoidFunc u, VoidFunc v,
    VoidFunc w, VoidFunc x);
}

class IrredLoopNoGoto extends IrredLoop
{
    public void invoke(boolean u_start,
    IntFunc w_cond, IntFunc x_cond,
    VoidFunc u, VoidFunc v,
    VoidFunc w, VoidFunc x)
    {
        boolean is_end = false, v_first = !u_start;
        do {
            if (!v_first) u.invoke();
            do {
                if (!v_first) {
                    w.invoke();
                    boolean loop = false;
                    switch (w_cond.invoke()) {
                    case EXIT: is_end = true;
                    case LOOP: loop = true;
                    }
                    if (loop) break;
                }
                do {
                    if (!v_first) {
                        x.invoke();
                        boolean loop = false;
                        switch (x_cond.invoke()) {
                        case EXIT: is_end = true;
                        case LOOP: loop = true;
                        }
                        if (loop) break;
                    }
                    v.invoke();
                    v_first = false;
                } while (true);
            } while (!is_end);
        } while (!is_end);
    }    
}

class IrredLoopGotoVM extends IrredLoop
{
    interface Instruction //opcodes
    {
        public int invoke();
    }
    class Jump implements Instruction
    {
        private int loc;
        public Jump(int loc) { this.loc = loc; }
        public int invoke() { return loc; }
    }
    class CondJump implements Instruction
    {
        private boolean cond;
        private int loc;
        public CondJump(boolean cond, int loc) { this.cond = cond; this.loc = loc; }
        public int invoke() { return cond ? loc : -1; }
    }
    class JumpTable implements Instruction
    {
        private IntFunc cond;
        private int[] locs;
        public JumpTable(IntFunc cond, int[] locs) { this.cond = cond; this.locs = locs; }
        public int invoke() { return locs[cond.invoke()]; }
    }
    class CallLambda implements Instruction
    {
        VoidFunc func;
        public CallLambda(VoidFunc func) { this.func = func; }
        public int invoke() { func.invoke(); return -1; }
    }

    public void invoke(boolean u_start,
    IntFunc w_cond, IntFunc x_cond,
    VoidFunc u, VoidFunc v,
    VoidFunc w, VoidFunc x)
    {
        int do_u = 1, do_w = 2, do_x = 4, do_v = 6, end = 8;
        Instruction[] code = {
            new CondJump(!u_start, do_v), //0
            new CallLambda(u), //1=do_u
            new CallLambda(w), //2=do_w
            new JumpTable(w_cond, new int[] {end, do_u, do_x}), //3
            new CallLambda(x), //4=do_x
            new JumpTable(x_cond, new int[] {end, do_w, do_v}), //5
            new CallLambda(v), //6 = do_v
            new Jump(do_x) //7, end is 8
        };
        int instptr = 0;
        while (true) {
            int ninstptr = code[instptr].invoke();
            instptr = ninstptr == -1 ? instptr + 1 : ninstptr;
            if (instptr >= code.length) break;
        }
    }
}

class JSMC
{
    //https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.35.8991&rep=rep1&type=pdf
    public static void test_irreducible()
    {
        IrredLoop ilt[] = { new IrredLoopNoGoto(),
            new IrredLoopGotoVM() };
        Random r = new Random();
        for (int i = 0; i < ilt.length; i++) {
            r.setSeed(5);
            VoidFunc u = new VoidFunc(), v = new VoidFunc(), w = new VoidFunc(), x = new VoidFunc();
            ilt[i].invoke(r.nextInt(2) == 1, new IntFunc(r),
                new IntFunc(r), u, v, w, x);
            System.out.println(u.data + " " + v.data + " " + w.data + " " + x.data);
        }
    }

    public static void main(String[] args)
    {
        test_irreducible();
    }
}