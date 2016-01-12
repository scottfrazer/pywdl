import wdl
import argparse

from wdl.binding import *

def run():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input_file', help='Input wdl file', required=True, dest='input_file')
	parser.add_argument('-o', '--output_file', help='Output dot file', required=True, dest='output_file')
	args = parser.parse_args()

	fp = open(args.input_file)

	wdl_namespace = wdl.load(fp)

	output = open(args.output_file, 'w')
	output.write('digraph {\n')

	links = []
	scatter_nodes = set()

	for workflow in wdl_namespace.workflows:
		for call in workflow.calls():
			for downstream in call.downstream():
				if isinstance(downstream, Call):
					links.append((call.name, downstream.name))
			if not isinstance(call.parent, Workflow):
				scatter_nodes.add(call.parent)

	for scatter in scatter_nodes:
		for parent in reversed(scope_hierarchy(scatter)):
			if not isinstance(parent, Workflow):
				output.write('subgraph cluster_%s {\n' % parent.name)

		call_nodes = [call.name for call in scatter.upstream() if isinstance(call, Call)]
		if call_nodes:
			output.write('edge [style=invis]\n')
			output.write('"%s_label" [margin=0 shape="none" label="%s"]\n' % (scatter.name, '\\n'.join(call_nodes)))

		for downstream in scatter.downstream():
			if isinstance(downstream, Call):
				output.write('\t"%s"\n' % downstream.name)
				if call_nodes:
					output.write('\t"%s_label"->"%s"' % (scatter.name, downstream.name))

		for parent in scope_hierarchy(scatter):
			if not isinstance(parent, Workflow):
				output.write('}\n')

	for from_node, to_node in links:
		output.write('"%s"->"%s"\n' % (from_node, to_node))

	output.write('labelloc="t"\n')
	#TODO: If there are multiple workflows this only uses the first for the title of the graph
	output.write('label="%s"\n' % wdl_namespace.workflows[0].name)
	output.write('}')

	output.close()
	fp.close()

if __name__ == '__main__':
    run()