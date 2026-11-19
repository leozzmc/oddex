// Decompiles the functions named in the script arguments and prints their C.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Symbol;

public class DecompileFns extends GhidraScript {
    @Override
    public void run() throws Exception {
        DecompInterface ifc = new DecompInterface();
        ifc.openProgram(currentProgram);
        for (String name : getScriptArgs()) {
            Function f = null;
            for (Symbol s : currentProgram.getSymbolTable().getSymbols(name)) {
                Address a = s.getAddress();
                f = getFunctionAt(a);
                if (f == null) {
                    disassemble(a);
                    f = createFunction(a, name);
                }
                break;
            }
            if (f == null) {
                println("NOT FOUND " + name);
                continue;
            }
            DecompileResults r = ifc.decompileFunction(f, 60, monitor);
            println("===== " + name + " @ " + f.getEntryPoint());
            println(r.getDecompiledFunction() == null ? r.getErrorMessage() : r.getDecompiledFunction().getC());
        }
        ifc.dispose();
    }
}
