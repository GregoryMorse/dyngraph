static get_path_name(filepath)
{
	auto i = strlen(filepath) - 1;
	while (i != 0 && filepath[i] != "\\" && filepath[i] != "/") {
		i--;
	}
	return i == 0 ? filepath : filepath[:i];
}
static remove_bad_chars(name)
{
	auto filtered = "";
	auto i = strlen(name);
	auto c = 0;
	while (c < i) {
		if (strstr("/<>:\"\\|?*", name[c]) == -1) {
			filtered = filtered + name[c];
		}
		c++;
	}
	return filtered;
}
static gen_graphs()
{
	auto p = get_path_name(get_idb_path());
	auto r = get_root_filename();
	//CHART_GEN_GDL = 0x4000
	//FUNCATTR_END = 8
	call_system("mkdir \"" + p + "/" + r + "\"");
	gen_simple_call_chart(p + "/" + r + "/" + "calls", "", 0x4000);
	auto a;
	a = get_next_func(0);
	while (a != -1) {
		gen_flow_graph(p + "/" + r + "/func_" + remove_bad_chars(get_func_name(a)), "", a, get_func_attr(get_next_func(a), 8), 0x4000);
		a = get_next_func(a);
	}
}