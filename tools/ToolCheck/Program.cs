using System.Diagnostics;

// Each check: a display name, the command to run, and its arguments.
var checks = new List<ToolCheck>
{
    new("Git", "git", "--version"),
    new(".NET SDK", "dotnet", "--version"),
    new("uv", "uv", "--version"),
    new("Python 3.12 (managed by uv)", "uv", "run --no-project --python 3.12 python --version"),
    new("Docker CLI", "docker", "--version"),
    new("Docker engine running", "docker", "info --format \"{{.ServerVersion}}\""),
    new("VS Code", "code", "--version"),
};

Console.WriteLine("Pathology platform toolchain check");
Console.WriteLine(new string('-', 70));

var failures = 0;
foreach (var check in checks)
{
    var result = Run(check.Command, check.Arguments);
    var status = result.Success ? "[ OK ]" : "[FAIL]";
    if (!result.Success)
    {
        failures++;
    }

    Console.WriteLine($"{status} {check.Name,-30} {result.FirstLine}");
}

Console.WriteLine(new string('-', 70));
Console.WriteLine(failures == 0 ? "All tools found." : $"{failures} check(s) failed.");
return failures == 0 ? 0 : 1;

static RunResult Run(string command, string arguments)
{
    // On Windows some tools (like VS Code's 'code') are .cmd scripts, which
    // Process.Start can't launch directly, so we run them through cmd.exe.
    var startInfo = OperatingSystem.IsWindows()
        ? new ProcessStartInfo("cmd.exe", $"/c {command} {arguments}")
        : new ProcessStartInfo(command, arguments);
    startInfo.RedirectStandardOutput = true;
    startInfo.RedirectStandardError = true;
    startInfo.UseShellExecute = false;

    try
    {
        using var process = Process.Start(startInfo)!;

        // Read both streams at the same time so neither can fill up and block the process.
        var outputTask = process.StandardOutput.ReadToEndAsync();
        var errorTask = process.StandardError.ReadToEndAsync();
        process.WaitForExit();

        var text = string.IsNullOrWhiteSpace(outputTask.Result) ? errorTask.Result : outputTask.Result;
        var firstLine = text
            .Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(line => line.Trim())
            .FirstOrDefault() ?? "";

        return new RunResult(process.ExitCode == 0, firstLine);
    }
    catch (System.ComponentModel.Win32Exception)
    {
        // Thrown on macOS/Linux when the command isn't on the PATH.
        return new RunResult(false, "not found on PATH");
    }
}

record ToolCheck(string Name, string Command, string Arguments);

record RunResult(bool Success, string FirstLine);